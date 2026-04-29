import React from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

export function HeroSection() {
  return (
    <section className="relative w-full py-24 md:py-32 lg:py-48 flex flex-col items-center justify-center text-center px-4 bg-gradient-to-b from-background to-muted overflow-hidden">
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
      
      <div className="z-10 flex flex-col items-center space-y-6 max-w-4xl">
        <Badge variant="secondary" className="px-4 py-1 text-sm rounded-full backdrop-blur-md bg-secondary/50 border-secondary/20">
          ✨ Introducing TACSOP 0
        </Badge>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-foreground">
          Build Faster with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-600">Precision</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl leading-relaxed">
          The ultimate boilerplate and deployment engine for your next big idea. Engineered for scale and design perfection.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 mt-8">
          <Button size="lg" className="h-12 px-8 text-lg rounded-full shadow-lg hover:shadow-xl transition-all">
            Get Started
          </Button>
          <Button size="lg" variant="outline" className="h-12 px-8 text-lg rounded-full backdrop-blur-md bg-background/50">
            Read Docs
          </Button>
        </div>
      </div>
    </section>
  );
}
