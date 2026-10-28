"""Fetch the reviewed public background with provenance and a fixed integrity check."""
import argparse,hashlib,json,subprocess,urllib.request
from pathlib import Path

URL='https://videos.pexels.com/video-files/8347238/8347238-uhd_2160_3840_25fps.mp4'
SHA256='47c2ecc4a76533f84d95ed0f88703df7e282d3c23ab730b38511bf1424258264'
PAGE='https://www.pexels.com/video/computers-on-the-office-table-8347238/'

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('artifacts/public-footage-001'))
 root=p.parse_args().output;root.mkdir(parents=True,exist_ok=True)
 source=root/'source.mp4'
 if not source.exists():
  temporary=root/'source.partial.mp4'
  try:
   with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'VEIL-demo/0.1'}),timeout=45) as response,temporary.open('wb') as out:
    total=0
    while chunk:=response.read(1024*1024):
     total+=len(chunk)
     if total>150*1024*1024:raise ValueError('Public download exceeds 150 MiB limit')
     out.write(chunk)
   if hashlib.sha256(temporary.read_bytes()).hexdigest()!=SHA256:raise ValueError('Public source hash changed; inspect before accepting a new asset')
   temporary.replace(source)
  finally:temporary.unlink(missing_ok=True)
 if hashlib.sha256(source.read_bytes()).hexdigest()!=SHA256:raise ValueError('Local source differs from reviewed asset')
 record={'source_page':PAGE,'download_url':URL,'creator':'Kampus Production','license':'https://www.pexels.com/license/',
   'source_sha256':SHA256,'downloaded_bytes':source.stat().st_size,'cloud_upload':False,
   'intended_use':'reviewed empty-office background; synthetic privacy targets only'}
 (root/'source-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-t','8','-vf','scale=360:640,fps=12','-an',
    '-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(root/'background.mp4')],check=True)
 print('Background ready; no cloud/model calls made.')
if __name__=='__main__':main()
