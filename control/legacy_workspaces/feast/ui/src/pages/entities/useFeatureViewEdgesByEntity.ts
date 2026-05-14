import type { EntityRelation } from "../../parsers/parseEntityRelationships";
import useLoadRelationshipData from "../../queries/useLoadRelationshipsData";

const entityGroupByName = (data: EntityRelation[]) => {
  return data
    .filter((edge) => {
      return edge.source.type === "entity";
    })
    .reduce((memo: Record<string, EntityRelation[]>, current) => {
      if (memo[current.source.name]) {
        memo[current.source.name].push(current);
      } else {
        memo[current.source.name] = [current];
      }

      return memo;
    }, {});
};

const useFeatureViewEdgesByEntity = () => {
  const query = useLoadRelationshipData();

  return {
    ...query,
    data: query.isSuccess && query.data ? entityGroupByName(query.data) : undefined,
  };
};

export default useFeatureViewEdgesByEntity;
