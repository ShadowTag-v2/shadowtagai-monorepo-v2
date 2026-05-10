import puppeteer from 'puppeteer-core';
import { PubSub } from '@google-cloud/pubsub';
import { GoogleGenAI } from '@google/genai';

const externalAi = new GoogleGenAI({});

export async function executeSubagentTask(prompt: string, targetUrl: string) {
    const pubsub = new PubSub({ projectId: 'shadowtag-omega-v4' });
    const browser = await puppeteer.connect({ browserURL: 'http://localhost:9222' });
    const page = await browser.newPage();
    
    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto(targetUrl, { waitUntil: 'networkidle2' });
    
    const domHtml = await page.content();
    console.log("⚡ [Gemini Flash-Lite] Analyzing DOM structure...");
    await externalAi.models.generateContent({
        model: 'gemini-3.1-flash-lite-preview',
        contents: `Analyze this DOM: ${domHtml.substring(0, 10000)}`,
        config: { thinkingConfig: { type: "high" } }
    });
    
    await page.mouse.click(450, 800); 
    await page.keyboard.type(prompt);
    
    await Bun.sleep(15000); 
    await browser.disconnect();
    await pubsub.topic('database-events').publishMessage({ data: Buffer.from('ASSETS_RENDERED') });
}
