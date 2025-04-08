import { InstantSearch, Highlight, Hits, RefinementList, HitsPerPage, Pagination } from "react-instantsearch";
import { SearchBox } from "react-instantsearch";
import TypesenseInstantSearchAdapter from "typesense-instantsearch-adapter";
import { Hit as AlgoliaHit } from 'instantsearch.js';
import { capitalize } from "./utils";


const typesenseInstantsearchAdapter = new TypesenseInstantSearchAdapter({
  server: {
    apiKey: "ZeCdqWKkRMNANvsvjej34mvkuuJHrape",
    nodes: [
      {
        host: "ub24tw9s6zhiv5njp-1.a1.typesense.net",
        port: 443,
        protocol: "https",
      },
    ],
    cacheSearchResultsForSeconds: 2 * 60, // Cache search results from server. Defaults to 2 minutes. Set to 0 to disable caching.
  },
  // The following parameters are directly passed to Typesense's search API endpoint.
  //  So you can pass any parameters supported by the search endpoint below.
  //  query_by is required.
  additionalSearchParameters: {
    query_by: "text",
  },
});
const searchClient = typesenseInstantsearchAdapter.searchClient;

type HitProps = {
  hit: AlgoliaHit<{
    id: string
    podcast: string
    episode: number
    speaker: string
    text: string
    line_number?: number
  }>;
};

function Hit({ hit }: HitProps) {
  const relLink = `${hit.podcast}/${hit.episode}`

  return (
    <div className="space-x-1">
      <span className="font-bold">{hit.speaker}&nbsp;</span>
      <Highlight hit={hit} attribute="text" />
      <a href={`https://changelog.com/${relLink}`} target="_blank" className="underline text-blue-600">({capitalize(hit.podcast)} {hit.episode})</a>
    </div>
  );
}

function App() {
  return (
    <>
      <div className="p-1">
        <InstantSearch indexName="transcripts" searchClient={searchClient}>
          <SearchBox classNames={{
            root: 'mb-2',
            form: 'space-x-1 flex items-center',
            input: 'border rounded p-1 text-xl flex-1',
            submit: 'hidden',
            submitIcon: 'mx-auto',
            reset: 'h-[38px] w-[38px] border rounded hover:cursor-pointer',
            resetIcon: 'mx-auto',
          }} />
          <div className="flex flex-wrap gap-3">
            <div className="space-y-3">
              <div>
                <label>Podcast</label>
                <RefinementList attribute="podcast" classNames={{
                  label: 'space-x-1',
                  count: 'hidden',
                }} />
              </div>
              <div>
                <label>Speaker</label>
                <RefinementList attribute="speaker" searchable classNames={{
                  label: 'space-x-1',
                  count: 'hidden',
                  searchBox: 'max-w-full [&_.ais-SearchBox-input]:max-w-full [&_.ais-SearchBox-input]:border [&_.ais-SearchBox-input]:rounded [&_.ais-SearchBox-submit]:hidden',
                }} />
              </div>
              <div>
                <label>Results per page</label>
                <HitsPerPage items={[
                  { label: '10', value: 10, default: true },
                  { label: '20', value: 20 },
                  { label: '50', value: 50 },
                ]} classNames={{
                  select: 'border rounded p-1'
                }} />
              </div>
              <div>
                <label>Page</label>
                <Pagination classNames={{
                  list: 'space-x-2',
                  item: 'inline',
                }} />
              </div>
            </div>
            <div className="flex-1 max-w-full">
              <Hits hitComponent={Hit} classNames={{
                list: 'space-y-2',
                emptyRoot: 'hidden',
              }} />
            </div>
          </div>
        </InstantSearch>
      </div>
    </>
  )
}

export default App
