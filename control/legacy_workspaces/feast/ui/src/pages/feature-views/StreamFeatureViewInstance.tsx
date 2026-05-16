import { EuiPageTemplate } from "@elastic/eui";
import React from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  useStreamFeatureViewCustomTabRoutes,
  useStreamFeatureViewCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { FeatureViewIcon } from "../../graphics/FeatureViewIcon";
import { useMatchExact } from "../../hooks/useMatchSubpath";
import type { feast } from "../../protos";
import StreamFeatureViewOverviewTab from "./StreamFeatureViewOverviewTab";

interface StreamFeatureInstanceProps {
  data: feast.core.IStreamFeatureView;
}

const StreamFeatureInstance = ({ data }: StreamFeatureInstanceProps) => {
  const navigate = useNavigate();
  const { featureViewName } = useParams();

  const { customNavigationTabs } = useStreamFeatureViewCustomTabs(navigate);
  const CustomTabRoutes = useStreamFeatureViewCustomTabRoutes();

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        paddingSize="l"
        iconType={FeatureViewIcon}
        pageTitle={`${featureViewName}`}
        tabs={[
          {
            label: "Overview",
            isSelected: useMatchExact(""),
            onClick: () => {
              navigate("");
            },
          },
          ...customNavigationTabs,
        ]}
      />
      <EuiPageTemplate.Section>
        <Routes>
          <Route path="/" element={<StreamFeatureViewOverviewTab data={data} />} />
          {CustomTabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default StreamFeatureInstance;
