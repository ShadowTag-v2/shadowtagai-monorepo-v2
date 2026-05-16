import { EuiPageTemplate } from "@elastic/eui";
import React from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  useFeatureCustomTabRoutes,
  useFeatureCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { FeatureIcon } from "../../graphics/FeatureIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useMatchExact } from "../../hooks/useMatchSubpath";
import FeatureOverviewTab from "./FeatureOverviewTab";

const FeatureInstance = () => {
  const navigate = useNavigate();
  const { FeatureViewName, FeatureName } = useParams();

  const { customNavigationTabs } = useFeatureCustomTabs(navigate);
  const CustomTabRoutes = useFeatureCustomTabRoutes();

  useDocumentTitle(`${FeatureName} | ${FeatureViewName} | Feast`);

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={FeatureIcon}
        pageTitle={`Feature: ${FeatureName}`}
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
          <Route path="/" element={<FeatureOverviewTab />} />
          {CustomTabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default FeatureInstance;
