import { EuiLoadingSpinner, EuiPageTemplate } from "@elastic/eui";
import React, { useContext } from "react";
import { useParams } from "react-router-dom";
import ExportButton from "../../components/ExportButton";
import RegistryPathContext from "../../contexts/RegistryPathContext";
import { EntityIcon } from "../../graphics/EntityIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import useLoadRegistry from "../../queries/useLoadRegistry";
import EntitiesListingTable from "./EntitiesListingTable";
import EntityIndexEmptyState from "./EntityIndexEmptyState";

const useLoadEntities = () => {
  const registryUrl = useContext(RegistryPathContext);
  const { projectName } = useParams();
  const registryQuery = useLoadRegistry(registryUrl, projectName);

  const data = registryQuery.data === undefined ? undefined : registryQuery.data.objects.entities;

  return {
    ...registryQuery,
    data,
  };
};

const Index = () => {
  const { isLoading, isSuccess, isError, data } = useLoadEntities();

  useDocumentTitle(`Entities | Feast`);

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={EntityIcon}
        pageTitle="Entities"
        rightSideItems={[<ExportButton data={data ?? []} fileName="entities" formats={["json"]} />]}
      />
      <EuiPageTemplate.Section>
        {isLoading && (
          <p>
            <EuiLoadingSpinner size="m" /> Loading
          </p>
        )}
        {isError && <p>We encountered an error while loading.</p>}
        {isSuccess && !data && <EntityIndexEmptyState />}
        {isSuccess && data && <EntitiesListingTable entities={data} />}
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default Index;
