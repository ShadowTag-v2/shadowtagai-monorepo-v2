import WalletConnect from "../components/WalletConnect";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-800 bg-black pb-6 pt-8 backdrop-blur-2xl lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-gray-800 lg:p-4">
          Antigravity Sovereign Economy
        </p>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-gray-900 via-gray-900 lg:static lg:h-auto lg:w-auto lg:bg-none">
          <WalletConnect />
        </div>
      </div>

      <div className="relative flex place-items-center before:absolute before:h-[300px] before:w-[480px] before:-translate-x-1/2 before:rounded-full before:bg-gradient-to-br before:from-purple-600 before:to-transparent before:blur-2xl before:content-[''] after:absolute after:-z-20 after:h-[180px] after:w-[240px] after:translate-x-1/3 after:bg-gradient-to-tr after:from-cyan-500 after:to-transparent after:blur-2xl after:content-['']">
        <h1 className="text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
          MINT YOUR IDENTITY
        </h1>
      </div>

      <div className="mb-32 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-3 lg:text-left gap-4">
        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-700 hover:bg-gray-800/30">
          <h2 className="mb-3 text-2xl font-semibold">
            Tokenize{" "}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Mint your $SOV tokens backed by computational work.
          </p>
        </div>

        <div className="group rounded-lg border border-gray-700 bg-gray-800 px-5 py-4 transition-colors">
          <h2 className="mb-3 text-2xl font-semibold text-green-400">Purchase NFT</h2>
          <p className="mb-4 text-sm opacity-50">Unlock Tier 1 Access.</p>
          <button className="bg-white text-black font-bold py-2 px-4 rounded hover:bg-gray-200 w-full">
            Buy Now (Stripe)
          </button>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-700 hover:bg-gray-800/30">
          <h2 className="mb-3 text-2xl font-semibold">
            Governance{" "}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Vote on Swarm protocol upgrades with Judge 6.
          </p>
        </div>
      </div>
    </main>
  );
}
