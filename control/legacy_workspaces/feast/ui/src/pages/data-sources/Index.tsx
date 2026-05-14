import {
  EuiFieldSearch,
  EuiFlexGroup,
  EuiFlexItem,
  EuiLoadingSpinner,
  EuiPageTemplate,
  EuiSpacer,
  EuiTitle,
} from "@elastic/eui";
import React, { useContext } from "react";
import { useParams } from "react-router-dom";
import ExportButton from "../../components/ExportButton";
import RegistryPathContext from "../../contexts/RegistryPathContext";
import { DataSourceIcon } from "../../graphics/DataSourceIcon";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useSearchQuery } from "../../hooks/useSearchInputWithTags";
import type { feast } from "../../protos";
import useLoadRegistry from "../../queries/useLoadRegistry";
import DataSourceIndexEmptyState from "./DataSourceIndexEmptyState";
import DatasourcesListingTable from "./DataSourcesListingTable";

const useLoadDatasources = () => {
  const registryUrl = useContext(RegistryPathContext);
  const { projectName } = useParams();
  const registryQuery = useLoadRegistry(registryUrl, projectName);

  const data =
    registryQuery.data === undefined ? undefined : registryQuery.data.objects.dataSources;

  return {
    ...registryQuery,
    data,
  };
};

const filterFn = (data: feast.core.IDataSource[], searchTokens: string[]) => {
  const filteredByTags = data;

  if (searchTokens.length) {
    return filteredByTags.filter((entry) => {
      return searchTokens.find((token) => {
        return token.length >= 3 && entry.name && entry.name.indexOf(token) >= 0;
      });
    });
  }

  return filteredByTags;
};

const Index = () => {
  const { isLoading, isSuccess, isError, data } = useLoadDatasources();

  useDocumentTitle(`Data Sources | Feast`);

  const { searchString, searchTokens, setSearchString } = useSearchQuery();

  const filterResult = data ? filterFn(data, searchTokens) : data;

  return (
    <EuiPageTemplate panelled>
      <EuiPageTemplate.Header
        restrictWidth
        iconType={DataSourceIcon}
        pageTitle="Data Sources"
        rightSideItems={[
          <ExportButton data={filterResult ?? []} fileName="data_sources" formats={["json"]} />,
        ]}
      />
      <EuiPageTemplate.Section>
        {isLoading && (
          <p>
            <EuiLoadingSpinner size="m" /> Loading
          </p>
        )}
        {isError && <p>We encountered an error while loading.</p>}
        {isSuccess && !data && <DataSourceIndexEmptyState />}
        {isSuccess && data && data.length > 0 && filterResult && (
          <React.Fragment>
            <EuiFlexGroup>
              <EuiFlexItem grow={2}>
                <EuiTitle size="xs">
                  <h2>Search</h2>
                </EuiTitle>
                <EuiFieldSearch
                  value={searchString}
                  fullWidth={true}
                  onChange={(e) => {
                    setSearchString(e.target.value);
                  }}
                />
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer size="m" />
            <DatasourcesListingTable dataSources={filterResult} />
          </React.Fragment>
        )}
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};

export default Index;
