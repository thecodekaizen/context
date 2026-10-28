"""Provider-independent, frame-aligned privacy geometry."""
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,FiniteFloat,model_validator

class StrictModel(BaseModel):model_config=ConfigDict(extra='forbid')
class FrameRegion(StrictModel):
 frame:int=Field(ge=0)
 box:tuple[FiniteFloat,FiniteFloat,FiniteFloat,FiniteFloat]
 confidence:FiniteFloat|None=None
 @model_validator(mode='after')
 def valid(self):
  x1,y1,x2,y2=self.box
  if x1<0 or y1<0 or x2<=x1 or y2<=y1:raise ValueError('Invalid region bounds')
  if self.confidence is not None and not 0<=self.confidence<=1:raise ValueError('Invalid confidence')
  return self
class VisualTrack(StrictModel):
 id:str
 category:Literal['face','license_plate','phone_number']
 source:str
 action:Literal['cover']='cover'
 regions:list[FrameRegion]
class AudioInterval(StrictModel):
 start_ms:int=Field(ge=0)
 end_ms:int=Field(gt=0)
 category:Literal['spoken_phone']='spoken_phone'
 source:str='muse-voice-transcribe-1.0'
 @model_validator(mode='after')
 def valid(self):
  if self.end_ms<=self.start_ms:raise ValueError('Invalid audio interval')
  return self
class Timeline(StrictModel):
 duration_ms:int=Field(gt=0)
 fps:FiniteFloat=Field(gt=0)
 width:int=Field(gt=0)
 height:int=Field(gt=0)
 visual_tracks:list[VisualTrack]
 audio_intervals:list[AudioInterval]
