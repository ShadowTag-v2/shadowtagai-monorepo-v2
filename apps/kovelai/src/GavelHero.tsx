import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useStitchTheme } from '@google-labs-code/stitch-sdk'; 
import { useAuth } from '../core/auth'; 
import { graphql, useLazyLoadQuery, useSubscription } from 'react-relay'; 

const UserAccessQuery = graphql`
  query GavelHeroAccessQuery($uid: String!) { userAccess(firebaseUid: $uid) }
`;
const PaymentSubscription = graphql`
  subscription GavelHeroPaymentSubscription($uid: String!) { paymentCleared(firebaseUid: $uid) }
`;

const FRAME_COUNT = 142; 
const CDN_BASE_URL = 'https://storage.googleapis.com/shadowtag-omega-v4-cdn'; 

export const GavelHero: React.FC = () => {
    const theme = useStitchTheme(); 
    const { user, loading: authLoading } = useAuth(); 
    
    // Native Relay Querying & Real-Time CDC Subscription
    const data = useLazyLoadQuery<any>(UserAccessQuery, { uid: user?.uid ?? "" }, { fetchPolicy: 'store-or-network' });
    const subConfig = useMemo(() => ({ subscription: PaymentSubscription, variables: { uid: user?.uid ?? "" } }), [user]);
    useSubscription(subConfig);
    
    const isAuthorized = data?.userAccess;
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        if (!isAuthorized || !canvasRef.current) return;
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        let frameIndex = 0; let animationFrameId: number;
        const images: HTMLImageElement[] = Array.from({ length: FRAME_COUNT }, (_, i) => {
            const img = new Image(); img.crossOrigin = "Anonymous"; img.src = `${CDN_BASE_URL}/frames/frame_${String(i + 1).padStart(4, '0')}.png`; return img;
        });

        const render = () => {
            if (images[frameIndex].complete && images[frameIndex].naturalWidth > 0) {
                if (!loaded) setLoaded(true);
                canvasRef.current!.width = images[frameIndex].naturalWidth; 
                canvasRef.current!.height = images[frameIndex].naturalHeight;
                ctx.drawImage(images[frameIndex], 0, 0);
            }
            frameIndex = (frameIndex + 1) % FRAME_COUNT;
            setTimeout(() => { animationFrameId = requestAnimationFrame(render); }, 1000 / 30);
        };
        render(); return () => cancelAnimationFrame(animationFrameId);
    }, [isAuthorized]);

    if (authLoading) return <div style={{ color: theme.colors.onSurface }}>Authenticating Lakeport Core...</div>;
    if (!user) return <div style={{ color: theme.colors.error }}>Identity required. Firebase Auth pending.</div>;
    if (!isAuthorized) return <div style={{ color: theme.colors.error }}>Spanner Ledger Denies Access. Awaiting Realtime CDC.</div>;

    return (
        <div style={{ backgroundColor: theme.colors.surface }} className="relative w-full h-screen flex justify-center items-center">
            {!loaded && <div style={{ color: theme.colors.onSurface, fontFamily: theme.typography.displayLarge }} className="absolute animate-pulse">Loading V19 Relay OS...</div>}
            <canvas ref={canvasRef} className={`w-full h-full object-cover transition-opacity duration-1000 ${loaded ? 'opacity-100' : 'opacity-0'}`} />
            <button style={{ backgroundColor: theme.colors.primary, color: theme.colors.onPrimary, borderRadius: theme.shapes.cornerFull }} className="absolute bottom-10 px-6 py-2 shadow-md">
                Execute Archon-Boot
            </button>
        </div>
    );
};
