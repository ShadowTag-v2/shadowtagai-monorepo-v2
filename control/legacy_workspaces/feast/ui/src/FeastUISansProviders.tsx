import React from "react";

import "./index.css";

import { EuiErrorBoundary, EuiProvider } from "@elastic/eui";
import { Route, Routes } from "react-router-dom";
import NoProjectGuard from "./components/NoProjectGuard";
import FeatureFlagsContext, { type FeatureFlags } from "./contexts/FeatureFlagsContext";
import {
  ProjectListContext,
  type ProjectsListContextInterface,
} from "./contexts/ProjectListContext";
import { ThemeProvider, useTheme } from "./contexts/ThemeContext";
import TabsRegistryContext, {
  type FeastTabsRegistryInterface,
} from "./custom-tabs/TabsRegistryContext";
import DataSourceInstance from "./pages/data-sources/DataSourceInstance";
import DatasourceIndex from "./pages/data-sources/Index";
import DocumentLabelingPage from "./pages/document-labeling/DocumentLabelingPage";
import EntityInstance from "./pages/entities/EntityInstance";
import EntityIndex from "./pages/entities/Index";
import FeatureServiceInstance from "./pages/feature-services/FeatureServiceInstance";
import FeatureServiceIndex from "./pages/feature-services/Index";
import CurlGeneratorTab from "./pages/feature-views/CurlGeneratorTab";
import FeatureViewInstance from "./pages/feature-views/FeatureViewInstance";
import FeatureViewIndex from "./pages/feature-views/Index";
import FeatureInstance from "./pages/features/FeatureInstance";
import FeatureListPage from "./pages/features/FeatureListPage";
import Layout from "./pages/Layout";
import LineageIndex from "./pages/lineage/Index";
import NoMatch from "./pages/NoMatch";
import ProjectOverviewPage from "./pages/ProjectOverviewPage";
import PermissionsIndex from "./pages/permissions/Index";
import RootProjectSelectionPage from "./pages/RootProjectSelectionPage";
import DatasetInstance from "./pages/saved-data-sets/DatasetInstance";
import DatasetIndex from "./pages/saved-data-sets/Index";

interface FeastUIConfigs {
  tabsRegistry?: FeastTabsRegistryInterface;
  featureFlags?: FeatureFlags;
  projectListPromise?: Promise<any>;
}

const defaultProjectListPromise = (basename: string) => {
  return fetch(`${basename}/projects-list.json`, {
    headers: {
      "Content-Type": "application/json",
    },
  }).then((res) => {
    return res.json();
  });
};

const FeastUISansProviders = ({
  basename = "",
  feastUIConfigs,
}: {
  basename?: string;
  feastUIConfigs?: FeastUIConfigs;
}) => {
  const projectListContext: ProjectsListContextInterface = feastUIConfigs?.projectListPromise
    ? {
        projectsListPromise: feastUIConfigs?.projectListPromise,
        isCustom: true,
      }
    : {
        projectsListPromise: defaultProjectListPromise(basename),
        isCustom: false,
      };

  return (
    <ThemeProvider>
      <FeastUISansProvidersInner
        basename={basename}
        projectListContext={projectListContext}
        feastUIConfigs={feastUIConfigs}
      />
    </ThemeProvider>
  );
};

const FeastUISansProvidersInner = ({
  basename,
  projectListContext,
  feastUIConfigs,
}: {
  basename: string;
  projectListContext: ProjectsListContextInterface;
  feastUIConfigs?: FeastUIConfigs;
}) => {
  const { colorMode } = useTheme();

  return (
    <EuiProvider colorMode={colorMode}>
      <EuiErrorBoundary>
        <TabsRegistryContext.Provider
          value={{
            RegularFeatureViewCustomTabs: [
              {
                label: "CURL Generator",
                path: "curl-generator",
                Component: CurlGeneratorTab,
              },
              ...(feastUIConfigs?.tabsRegistry?.RegularFeatureViewCustomTabs || []),
            ],
            OnDemandFeatureViewCustomTabs:
              feastUIConfigs?.tabsRegistry?.OnDemandFeatureViewCustomTabs || [],
            StreamFeatureViewCustomTabs:
              feastUIConfigs?.tabsRegistry?.StreamFeatureViewCustomTabs || [],
            FeatureServiceCustomTabs: feastUIConfigs?.tabsRegistry?.FeatureServiceCustomTabs || [],
            FeatureCustomTabs: feastUIConfigs?.tabsRegistry?.FeatureCustomTabs || [],
            DataSourceCustomTabs: feastUIConfigs?.tabsRegistry?.DataSourceCustomTabs || [],
            EntityCustomTabs: feastUIConfigs?.tabsRegistry?.EntityCustomTabs || [],
            DatasetCustomTabs: feastUIConfigs?.tabsRegistry?.DatasetCustomTabs || [],
          }}
        >
          <FeatureFlagsContext.Provider value={feastUIConfigs?.featureFlags || {}}>
            <ProjectListContext.Provider value={projectListContext}>
              <Routes>
                <Route path="/" element={<Layout />}>
                  <Route index element={<RootProjectSelectionPage />} />
                  <Route path="/p/:projectName/*" element={<NoProjectGuard />}>
                    <Route index element={<ProjectOverviewPage />} />
                    <Route path="data-source/" element={<DatasourceIndex />} />
                    <Route path="data-source/:dataSourceName/*" element={<DataSourceInstance />} />
                    <Route path="features/" element={<FeatureListPage />} />
                    <Route path="feature-view/" element={<FeatureViewIndex />} />
                    <Route
                      path="feature-view/:featureViewName/*"
                      element={<FeatureViewInstance />}
                    ></Route>
                    <Route
                      path="feature-view/:FeatureViewName/feature/:FeatureName/*"
                      element={<FeatureInstance />}
                    />
                    <Route path="feature-service/" element={<FeatureServiceIndex />} />
                    <Route
                      path="feature-service/:featureServiceName/*"
                      element={<FeatureServiceInstance />}
                    />
                    <Route path="entity/" element={<EntityIndex />} />
                    <Route path="entity/:entityName/*" element={<EntityInstance />} />

                    <Route path="data-set/" element={<DatasetIndex />} />
                    <Route path="data-set/:datasetName/*" element={<DatasetInstance />} />
                    <Route path="data-labeling/" element={<DocumentLabelingPage />} />
                    <Route path="permissions/" element={<PermissionsIndex />} />
                    <Route path="lineage/" element={<LineageIndex />} />
                  </Route>
                </Route>
                <Route path="*" element={<NoMatch />} />
              </Routes>
            </ProjectListContext.Provider>
          </FeatureFlagsContext.Provider>
        </TabsRegistryContext.Provider>
      </EuiErrorBoundary>
    </EuiProvider>
  );
};

export default FeastUISansProviders;
export type { FeastUIConfigs };
