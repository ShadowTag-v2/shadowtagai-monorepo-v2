import { Terminal } from 'lucide-react';
import type React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

export const TungstenLiveMonitorShadcn: React.FC<{ sessionId: string }> = ({ sessionId }) => {
  return (
    <Card className="w-full max-w-2xl bg-zinc-950 text-zinc-50 border-zinc-800">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Terminal className="h-4 w-4" />
          Tmux Session: {sessionId}
        </CardTitle>
        <Button variant="ghost" size="sm" className="h-8 text-zinc-400 hover:text-zinc-50">
          Minimize
        </Button>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[200px] w-full rounded-md border border-zinc-800 bg-black p-4 font-mono text-sm text-zinc-300">
          <div className="flex flex-col gap-1">
            <span>[2026-04-29T22:31:00Z] Background task initialized...</span>
            <span className="text-emerald-400">[2026-04-29T22:31:05Z] Waiting for stream...</span>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
