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
