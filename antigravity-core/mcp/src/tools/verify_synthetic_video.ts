import { executeGetVideoForensicsQuery } from '../utils/firebase-data-connect.js';

export async function verifySyntheticVideo(videoId: string, authToken: string) {
  try {
    // Direct query via Firebase Data Connect (Postgres)
    const data = await executeGetVideoForensicsQuery({ id: videoId });

    if (!data?.video) {
      return {
        content: [{ type: 'text', text: 'UNKNOWN: Video not found in HeadFade Truth Layer.' }],
      };
    }

    const analysis = {
      isSynthetic: true,
      humanDeceptionIndex: `${data.video.hdiScore}%`,
      foundationalModels: data.video.modelsUsed.join(' + '),
      remixParentCreator: data.video.parentCreatorId || 'Original Source',
      remixTree: data.video.remixTree || [],
    };

    return {
      content: [
        {
          type: 'text',
          text: `HEADFADE VERIFIED PROVENANCE: ${JSON.stringify(analysis, null, 2)}`,
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `ERROR: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
    };
  }
}
