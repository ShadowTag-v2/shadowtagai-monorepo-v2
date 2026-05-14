import {
  EuiDescriptionList,
  EuiDescriptionListDescription,
  EuiDescriptionListTitle,
  EuiFlexGroup,
  EuiFlexItem,
  EuiHorizontalRule,
  EuiLoadingSpinner,
  EuiPanel,
  EuiSpacer,
  EuiText,
  EuiTitle,
} from "@elastic/eui";
import React from "react";
import { useParams } from "react-router-dom";
import EuiCustomLink from "../../components/EuiCustomLink";
import TagsDisplay from "../../components/TagsDisplay";
import { feast } from "../../protos";
import useLoadFeature from "./useLoadFeature";

const FeatureOverviewTab = () => {
  const { projectName, FeatureViewName, FeatureName } = useParams();

  const eName = FeatureViewName === undefined ? "" : FeatureViewName;
  const fName = FeatureName === undefined ? "" : FeatureName;
  const { isLoading, isSuccess, isError, data, featureData } = useLoadFeature(eName, fName);
  const isEmpty = data === undefined || featureData === undefined;

  return (
    <React.Fragment>
      {isLoading && (
        <React.Fragment>
          <EuiLoadingSpinner size="m" /> Loading
        </React.Fragment>
      )}
      {isEmpty && (
        <p>
          No Feature with name {FeatureName} in FeatureView {FeatureViewName}
        </p>
      )}
      {isError && (
        <p>
          Error loading Feature {FeatureName} in FeatureView {FeatureViewName}
        </p>
      )}
      {isSuccess && data && (
        <React.Fragment>
          <EuiFlexGroup>
            <EuiFlexItem>
              <EuiPanel hasBorder={true}>
                <EuiTitle size="xs">
                  <h3>Properties</h3>
                </EuiTitle>
                <EuiHorizontalRule margin="xs" />
                <EuiDescriptionList>
                  <EuiDescriptionListTitle>Name</EuiDescriptionListTitle>
                  <EuiDescriptionListDescription>{featureData?.name}</EuiDescriptionListDescription>

                  <EuiDescriptionListTitle>Value Type</EuiDescriptionListTitle>
                  <EuiDescriptionListDescription>
                    {feast.types.ValueType.Enum[featureData?.valueType!]}
                  </EuiDescriptionListDescription>

                  <EuiDescriptionListTitle>Description</EuiDescriptionListTitle>
                  <EuiDescriptionListDescription>
                    {featureData?.description}
                  </EuiDescriptionListDescription>

                  <EuiDescriptionListTitle>FeatureView</EuiDescriptionListTitle>
                  <EuiDescriptionListDescription>
                    <EuiCustomLink to={`/p/${projectName}/feature-view/${FeatureViewName}`}>
                      {FeatureViewName}
                    </EuiCustomLink>
                  </EuiDescriptionListDescription>
                </EuiDescriptionList>
              </EuiPanel>
              <EuiSpacer size="m" />
              <EuiPanel hasBorder={true} grow={false}>
                <EuiTitle size="xs">
                  <h3>Tags</h3>
                </EuiTitle>
                <EuiHorizontalRule margin="xs" />
                {featureData?.tags ? (
                  <TagsDisplay tags={featureData.tags} />
                ) : (
                  <EuiText>No Tags specified on this field.</EuiText>
                )}
              </EuiPanel>
            </EuiFlexItem>
          </EuiFlexGroup>
        </React.Fragment>
      )}
    </React.Fragment>
  );
};
export default FeatureOverviewTab;
