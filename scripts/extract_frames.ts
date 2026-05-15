import { $ } from 'bun';

async function extractAndUpload(videoFile: string, outputDir: string) {
  const bucketName = 'shadowtag-omega-v4-cdn';
  console.log('⚡ [Bun] Extracting frames natively via FFmpeg...');

  await $`mkdir -p ${outputDir} && rm -rf ${outputDir}/*`;
  await $`ffmpeg -i ${videoFile} -vf "fps=30" ${outputDir}/frame_%04d.png -hide_banner -loglevel error`;

  console.log(`⚡ [Bun] Syncing frames to ${bucketName}...`);
  await $`gsutil -m rsync -d -r ${outputDir} gs://${bucketName}/frames`;
}
await extractAndUpload(process.argv[2], process.argv[3]);
