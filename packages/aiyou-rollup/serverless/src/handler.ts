import type { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';

export async function hello(event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> {
  const message = 'ShadowTag-v2 serverless starter online';
  return {
    statusCode: 200,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ message, time: new Date().toISOString() }),
  };
}
