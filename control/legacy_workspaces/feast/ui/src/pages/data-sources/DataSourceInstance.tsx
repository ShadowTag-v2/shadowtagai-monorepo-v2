import { EuiPageTemplate } from "@elastic/eui";
import React from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  useDataSourceCustomTabRoutes,
  useDataSourceCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { DataSourceIcon } from "../../graphics/DataSourceIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useMatchExact } from "../../hooks/useMatchSubpath";
import DataSourceOverviewTab from "./DataSourceOverviewTab";
import DataSourceRawData from "./DataSourceRawData";

const DataSourceInstance = () => {
  const navigate = useNavigate();
  const { dataSourceName } = useParams();

  useDocumentTitle(`${dataSourceName} | Data Source | Feast`);

  let tabs = [
    {
      label: "Overview",
      isSelected: useMatchExact(""),
      onClick: () => {
        navigate("");
      },
    },
  ];

  const { customNavigationTabs } = useDataSourceCustomTabs(navigate);
  tabs = tabs.concat(customNavigationTabs);

  const CustomTabRoutes = useDataSourceCustomTabRoutes();

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={DataSourceIcon}
        pageTitle={`Data Source: ${dataSourceName}`}
        tabs={tabs}
      />
      <EuiPageTemplate.Section>
        <Routes>
          <Route path="/" element={<DataSourceOverviewTab />} />
          <Route path="/raw-data" element={<DataSourceRawData />} />
          {CustomTabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default DataSourceInstance;
