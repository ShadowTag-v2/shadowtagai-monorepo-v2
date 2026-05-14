import { stringify } from "query-string";
import { encodeQueryParams } from "serialize-query-params";
import { StringParam } from "use-query-params";

const encodeSearchQueryString = (query: string) => {
  return stringify(
    encodeQueryParams(
      {
        tags: StringParam,
      },
      {
        tags: query,
      },
    ),
  );
};

export { encodeSearchQueryString };
