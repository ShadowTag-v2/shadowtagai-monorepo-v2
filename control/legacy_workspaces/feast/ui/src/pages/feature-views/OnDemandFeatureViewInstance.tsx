import { EuiPageTemplate } from "@elastic/eui";
import React from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  useOnDemandFeatureViewCustomTabRoutes,
  useOnDemandFeatureViewCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { FeatureViewIcon } from "../../graphics/FeatureViewIcon";
import { useMatchExact } from "../../hooks/useMatchSubpath";
import type { feast } from "../../protos";
import OnDemandFeatureViewOverviewTab from "./OnDemandFeatureViewOverviewTab";

interface OnDemandFeatureInstanceProps {
  data: feast.core.IOnDemandFeatureView;
}

const OnDemandFeatureInstance = ({ data }: OnDemandFeatureInstanceProps) => {
  const navigate = useNavigate();
  const { featureViewName } = useParams();

  const { customNavigationTabs } = useOnDemandFeatureViewCustomTabs(navigate);
  const CustomTabRoutes = useOnDemandFeatureViewCustomTabRoutes();

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
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
          <Route path="/" element={<OnDemandFeatureViewOverviewTab data={data} />} />
          {CustomTabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default OnDemandFeatureInstance;
