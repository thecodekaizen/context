import json
from pathlib import Path
import tempfile
import unittest
from thermal_investigator.investigation import Investigation
from thermal_investigator.investigator_tools import InvestigationTools,validate_tool_decision,decide_with_tools
from thermal_investigator.meta import MetaDecider
from thermal_investigator.physical import ThermalSpec,execute_model
from thermal_investigator.contracts import initial_schedule

MODEL={'specification':ThermalSpec(False).to_dict(),'estimated_parameters':dict(zip(ThermalSpec(False).parameter_names(),[.01,.01,.008,.008,.3,.25]))}

class InvestigatorToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.store=Investigation(self.root/'session.db');self.plan=initial_schedule()
        self.obs={'commands_fraction':self.plan.commands(),'temperature_c':execute_model(MODEL,self.plan.commands()).tolist(),
                  'ambient_c':22.,'sample_interval_s':2.,'source':'simulation','noise_std_c':.08,
                  'hidden_seed':12345,'answer_key':'secret-evaluation-label'}
        self.store.create('s',4,[self.obs]);self.store.add_model('s','v1',MODEL,['initial-0'])
        self.tools=InvestigationTools(self.store,'s',max_fits=2)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def decision(self,operation='fit_candidate',**updates):
        value={'context_id':self.tools.context()['context_id'],'operation':operation,'family':'linear' if operation=='fit_candidate' else None,
               'candidate_id':None,'model_id':None,'schedule_id':None,'kind':None,'evidence_ids':['initial-0'],'rationale':'Inspect observed prediction error.'}
        return {**value,**updates}
    def test_public_context_excludes_hidden_fields(self):
        encoded=json.dumps(self.tools.context())
        self.assertNotIn('hidden_seed',encoded);self.assertNotIn('secret-evaluation-label',encoded)
    def test_fit_cached_across_restart(self):
        result=self.tools.apply('fit-1',self.decision())
        self.store.close();self.store=Investigation(self.root/'session.db');self.tools=InvestigationTools(self.store,'s',max_fits=2)
        self.assertEqual(self.tools.fit('linear',['initial-0']),result)
        self.assertEqual(self.tools.fit_remaining(),1)
        with self.assertRaises(ValueError):InvestigationTools(self.store,'s',max_fits=3)
    def test_stale_unknown_and_code_payload_rejected(self):
        value=self.decision();self.tools.fit('linear',['initial-0'])
        for bad in (value,self.decision(evidence_ids=['future']),self.decision(family=[]),{**self.decision(),'code':'run'}):
            with self.assertRaises(ValueError):validate_tool_decision(bad,self.tools.context())
    def test_proposal_does_not_charge_or_execute(self):
        result=self.tools.apply('proposal',self.decision('propose_experiment',model_id='v1',schedule_id='both-release',kind='diagnostic'))
        self.assertEqual(result['status'],'proposal_only')
        self.assertEqual(self.store.export('s')['session']['used'],1)
        self.assertEqual(self.store.export('s')['actions'],[])
    def test_revision_requires_measured_mismatch(self):
        fitted=self.tools.fit('linear',['initial-0'])
        with self.assertRaises(ValueError):self.tools.apply('revision',self.decision('register_revision',candidate_id=fitted['candidate_id'],model_id='v1'))
        self.store.prepare('s','probe','v1',self.plan.to_dict())
        wrong={**self.obs,'temperature_c':[[a+1,b+1] for a,b in self.obs['temperature_c']]}
        self.store.execute('s','probe',lambda *args:wrong)
        revised=self.tools.fit('linear',['initial-0','probe'])
        value=self.decision('register_revision',candidate_id=revised['candidate_id'],model_id='v1',evidence_ids=['initial-0','probe'])
        result=self.tools.apply('revision',value)
        self.assertEqual(result['status'],'revision_registered')
        self.assertEqual(self.tools.apply('revision',value),result)
    def test_provider_contract_uses_cache_no_real_network(self):
        decision=self.decision('stop');calls=[]
        def transport(payload):
            calls.append(json.loads(payload))
            return {'status':'completed','usage':{'input_tokens':100,'output_tokens':30},
                    'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'decision':decision})}]}]}
        provider=MetaDecider('fake-secret',self.root/'provider',max_calls=1,transport=transport)
        first,usage=decide_with_tools(provider,self.tools,'meta_direct')
        second,cached=decide_with_tools(provider,self.tools,'meta_direct')
        self.assertEqual(first,second);self.assertEqual(len(calls),1);self.assertTrue(cached['cache_hit'])
        self.assertNotIn('fake-secret',json.dumps(calls))
    def test_fit_cap_enforced(self):
        self.tools.fit('linear',['initial-0']);self.tools.fit('sensor_lag',['initial-0'])
        with self.assertRaises(ValueError):self.tools.fit('quadratic_loss',['initial-0'])
    def test_wire_branches_forbid_invalid_field_combinations(self):
        from thermal_investigator.investigator_tools import tool_wire_schema
        branches=tool_wire_schema(self.tools.context())['properties']['decision']['anyOf']
        proposal=next(b for b in branches if b['properties']['operation']['enum']==['propose_experiment'])
        self.assertEqual(proposal['properties']['family'],{'type':'null'})
        self.assertEqual(proposal['properties']['candidate_id'],{'type':'null'})
        with self.assertRaises(ValueError):validate_tool_decision(self.decision('propose_experiment',family='quadratic_loss',model_id='v1',schedule_id='left-stair',kind='diagnostic'),self.tools.context())

    def test_wire_cannot_confirm_unrevised_model(self):
        from thermal_investigator.investigator_tools import tool_wire_schema
        branches=tool_wire_schema(self.tools.context())['properties']['decision']['anyOf']
        proposals=[b for b in branches if b['properties']['operation']['enum']==['propose_experiment']]
        self.assertEqual(len(proposals),1)
        self.assertEqual(proposals[0]['properties']['kind']['enum'],['diagnostic'])
        with self.assertRaises(ValueError):validate_tool_decision(self.decision('propose_experiment',model_id='v1',schedule_id='both-release',kind='confirmation'),self.tools.context())
