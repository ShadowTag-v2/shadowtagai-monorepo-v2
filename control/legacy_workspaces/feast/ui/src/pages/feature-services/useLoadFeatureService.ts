import { useContext } from "react";
import { useParams } from "react-router-dom";
import RegistryPathContext from "../../contexts/RegistryPathContext";
import type { EntityReference } from "../../parsers/parseEntityRelationships";
import { FEAST_FCO_TYPES } from "../../parsers/types";
import useLoadRegistry from "../../queries/useLoadRegistry";

const useLoadFeatureService = (featureServiceName: string) => {
  const registryUrl = useContext(RegistryPathContext);
  const { projectName } = useParams();
  const registryQuery = useLoadRegistry(registryUrl, projectName);

  const data =
    registryQuery.data === undefined
      ? undefined
      : registryQuery.data.objects.featureServices?.find(
          (fs) => fs?.spec?.name === featureServiceName,
        );

  let entities =
    data === undefined
      ? undefined
      : registryQuery.data?.indirectRelationships
          .filter((relationship) => {
            return (
              relationship.target.type === FEAST_FCO_TYPES.featureService &&
              relationship.target.name === data?.spec?.name &&
              relationship.source.type === FEAST_FCO_TYPES.entity
            );
          })
          .map((relationship) => {
            return relationship.source;
          });
  // Deduplicate on name of entity
  if (entities) {
    const entityToName: { [key: string]: EntityReference } = {};
    for (const entity of entities) {
      entityToName[entity.name] = entity;
    }
    entities = Object.values(entityToName);
  }
  return {
    ...registryQuery,
    data: data
      ? {
          ...data,
          permissions: registryQuery.data?.permissions,
        }
      : undefined,
    entities,
  };
};

export default useLoadFeatureService;
