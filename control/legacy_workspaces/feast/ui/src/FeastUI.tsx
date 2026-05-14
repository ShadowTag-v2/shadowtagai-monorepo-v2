import React from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import { BrowserRouter } from "react-router-dom";
import { QueryParamProvider } from "use-query-params";
import { ReactRouter6Adapter } from "use-query-params/adapters/react-router-6";
import FeastUISansProviders, { type FeastUIConfigs } from "./FeastUISansProviders";

interface FeastUIProps {
  reactQueryClient?: QueryClient;
  feastUIConfigs?: FeastUIConfigs;
}

const defaultQueryClient = new QueryClient();

const FeastUI = ({ reactQueryClient, feastUIConfigs }: FeastUIProps) => {
  const queryClient = reactQueryClient || defaultQueryClient;
  const basename = process.env.PUBLIC_URL ?? "";

  return (
    // Disable v7_relativeSplatPath: custom tab routes don't currently work with it
    <BrowserRouter
      basename={basename}
      future={{ v7_relativeSplatPath: false, v7_startTransition: true }}
    >
      <QueryClientProvider client={queryClient}>
        <QueryParamProvider adapter={ReactRouter6Adapter}>
          <FeastUISansProviders basename={basename} feastUIConfigs={feastUIConfigs} />
        </QueryParamProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

export default FeastUI;
export type { FeastUIConfigs };
