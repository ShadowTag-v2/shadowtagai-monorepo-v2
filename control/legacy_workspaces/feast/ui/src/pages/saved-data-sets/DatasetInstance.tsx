import { EuiPageTemplate } from "@elastic/eui";
import React from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  useDataSourceCustomTabRoutes,
  useDatasetCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { DatasetIcon } from "../../graphics/DatasetIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useMatchExact, useMatchSubpath } from "../../hooks/useMatchSubpath";
import DatasetExpectationsTab from "./DatasetExpectationsTab";
import DatasetOverviewTab from "./DatasetOverviewTab";

const DatasetInstance = () => {
  const navigate = useNavigate();
  const { datasetName } = useParams();

  useDocumentTitle(`${datasetName} | Saved Datasets | Feast`);

  const { customNavigationTabs } = useDatasetCustomTabs(navigate);
  const CustomTabRoutes = useDataSourceCustomTabRoutes();

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={DatasetIcon}
        pageTitle={`Entity: ${datasetName}`}
        tabs={[
          {
            label: "Overview",
            isSelected: useMatchExact(""),
            onClick: () => {
              navigate("");
            },
          },
          {
            label: "Expectations",
            isSelected: useMatchSubpath("expectations"),
            onClick: () => {
              navigate("expectations");
            },
          },
          ...customNavigationTabs,
        ]}
      />
      <EuiPageTemplate.Section>
        <Routes>
          <Route path="/" element={<DatasetOverviewTab />} />
          <Route path="/expectations" element={<DatasetExpectationsTab />} />
          {CustomTabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default DatasetInstance;
