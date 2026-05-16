import { EuiLoadingSpinner, EuiPageTemplate } from "@elastic/eui";
import React, { useContext } from "react";
import RegistryPathContext from "../../contexts/RegistryPathContext";
import { DatasetIcon } from "../../graphics/DatasetIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import useLoadRegistry from "../../queries/useLoadRegistry";
import DatasetsIndexEmptyState from "./DatasetsIndexEmptyState";
import DatasetsListingTable from "./DatasetsListingTable";

const useLoadSavedDataSets = () => {
  const registryUrl = useContext(RegistryPathContext);
  const registryQuery = useLoadRegistry(registryUrl);

  const data =
    registryQuery.data === undefined ? undefined : registryQuery.data.objects.savedDatasets;

  return {
    ...registryQuery,
    data,
  };
};

const Index = () => {
  const { isLoading, isSuccess, isError, data } = useLoadSavedDataSets();

  useDocumentTitle(`Saved Datasets | Feast`);

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header restrictWidth iconType={DatasetIcon} pageTitle="Datasets" />
      <EuiPageTemplate.Section>
        {isLoading && (
          <p>
            <EuiLoadingSpinner size="m" /> Loading
          </p>
        )}
        {isError && <p>We encountered an error while loading.</p>}
        {isSuccess && data && <DatasetsListingTable datasets={data} />}
        {isSuccess && !data && <DatasetsIndexEmptyState />}
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default Index;
