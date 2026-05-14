import { EuiPageTemplate } from "@elastic/eui";
import React from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  useEntityCustomTabRoutes,
  useEntityCustomTabs,
} from "../../custom-tabs/TabsRegistryContext";
import { EntityIcon } from "../../graphics/EntityIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useMatchExact } from "../../hooks/useMatchSubpath";
import EntityOverviewTab from "./EntityOverviewTab";

const EntityInstance = () => {
  const navigate = useNavigate();
  const { entityName } = useParams();

  const { customNavigationTabs } = useEntityCustomTabs(navigate);
  const CustomTabRoutes = useEntityCustomTabRoutes();

  useDocumentTitle(`${entityName} | Entity | Feast`);

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={EntityIcon}
        pageTitle={`Entity: ${entityName}`}
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
          <Route path="/" element={<EntityOverviewTab />} />
          {CustomTabRoutes}
        </Routes>
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default EntityInstance;
