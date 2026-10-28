import {test,expect} from '@playwright/test';
test('generated evidence, omission reveal and download',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');
 await expect(page.getByRole('heading',{name:/Every cut leaves/})).toBeVisible();
 await page.getByRole('button',{name:'Try generated case'}).click();
 await expect(page.getByText('Visual source correspondence found')).toBeVisible();
 await expect(page.getByRole('heading',{name:'4.00 seconds outside the published edit'})).toBeVisible();
 await expect(page.locator('video')).toHaveCount(2);
 await page.getByRole('button',{name:'Reveal missing context'}).click();
 await expect(page.getByText('REVEALING OMITTED CONTEXT')).toBeVisible();
 const source=page.locator('video').nth(1);
 await expect.poll(()=>source.evaluate((v:HTMLVideoElement)=>v.currentTime)).toBeGreaterThanOrEqual(4);
 await expect.poll(()=>source.evaluate((v:HTMLVideoElement)=>v.readyState)).toBeGreaterThanOrEqual(2);
 const href=await page.getByText('Download evidence JSON').getAttribute('href');
 const evidence=await (await page.request.get(href!)).json();
 expect(evidence.findings[0]).toMatchObject({kind:'omission',source_start:4,source_end:8});
 await page.screenshot({path:'../docs/workstation.png',fullPage:true});
 expect(errors).toEqual([]);
});
test('mobile workspace fits viewport',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
});
test('missing Meta credential is explicit and preserves evidence',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Try generated case'}).click();
 await expect(page.getByText('Visual source correspondence found')).toBeVisible();
 await page.getByRole('button',{name:'Review with Meta AI'}).click();
 await expect(page.getByRole('alert')).toContainText('MODEL_API_KEY');
 await expect(page.getByRole('heading',{name:'4.00 seconds outside the published edit'})).toBeVisible();
 await page.getByRole('button',{name:'Reveal missing context'}).click();
 await expect(page.getByText('REVEALING OMITTED CONTEXT')).toBeVisible();
});
test('model review presentation and citation seeking using a labeled test response',async({page})=>{
 await page.route('**/api/investigations/*/interpret/*',route=>route.fulfill({json:{model:'TEST RESPONSE',finding_id:'f0',interpretation:{observations:[{text:'Synthetic test observation',citations:[{media:'source',media_start:5,media_end:6,clip_id:'source_context'}]}],possible_effect:'Synthetic test interpretation',uncertainty:'This is a mocked UI test, not actual model inference.'}}}));
 await page.goto('/');await page.getByRole('button',{name:'Try generated case'}).click();
 await expect(page.getByText('Visual source correspondence found')).toBeVisible();
 await page.getByRole('button',{name:'Review with Meta AI'}).click();
 await expect(page.getByText('Synthetic test observation')).toBeVisible();
 await page.getByRole('button',{name:/Original 00:05.00/}).click();
 await expect.poll(()=>page.locator('video').nth(1).evaluate((v:HTMLVideoElement)=>v.currentTime)).toBe(5);
 await expect(page.getByText('Citation bounds checked. Model claims are not independently verified.')).toBeVisible();
});
