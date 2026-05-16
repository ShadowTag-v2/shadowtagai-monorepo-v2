import { EuiPageTemplate } from "@elastic/eui";
import React, { useContext } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import FeatureFlagsContext from "../../contexts/FeatureFlagsContext";
import {
  useRegularFeatureViewCustomTabRoutes,
  useRegularFeatureViewCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { FeatureViewIcon } from "../../graphics/FeatureViewIcon";
import { useMatchExact, useMatchSubpath } from "../../hooks/useMatchSubpath";
import type { feast } from "../../protos";
import FeatureViewLineageTab from "./FeatureViewLineageTab";
import RegularFeatureViewOverviewTab from "./RegularFeatureViewOverviewTab";

interface RegularFeatureInstanceProps {
  data: feast.core.IFeatureView;
  permissions?: any[];
}

const RegularFeatureInstance = ({ data, permissions }: RegularFeatureInstanceProps) => {
  const { enabledFeatureStatistics } = useContext(FeatureFlagsContext);
  const navigate = useNavigate();

  const { customNavigationTabs } = useRegularFeatureViewCustomTabs(navigate);
  const tabs = [
    {
      label: "Overview",
      isSelected: useMatchExact(""),
      onClick: () => {
        navigate("");
      },
    },
  ];

  tabs.push({
    label: "Lineage",
    isSelected: useMatchSubpath("lineage"),
    onClick: () => {
      navigate("lineage");
    },
  });

  const statisticsIsSelected = useMatchSubpath("statistics");
  if (enabledFeatureStatistics) {
    tabs.push({
      label: "Statistics",
      isSelected: statisticsIsSelected,
      onClick: () => {
        navigate("statistics");
      },
    });
  }

  tabs.push(...customNavigationTabs);

  const TabRoutes = useRegularFeatureViewCustomTabRoutes();

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={FeatureViewIcon}
        pageTitle={`${data?.spec?.name}`}
        tabs={tabs}
      />
      <EuiPageTemplate.Section>
        <Routes>
          <Route
            path="/"
            element={<RegularFeatureViewOverviewTab data={data} permissions={permissions} />}
          />
          <Route path="/lineage" element={<FeatureViewLineageTab data={data} />} />
          {TabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default RegularFeatureInstance;
