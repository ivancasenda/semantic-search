import { SearchState, StatusTypes } from './search.reducers';
import { selectSearchResult, selectLoadingStatus } from './search.selectors';

/**
 * Test suite for the SearchSelectors.
 */
describe('SearchSelectors', () => {
  /**
   * Initial state for testing.
   */
  const initialState: SearchState = {
    result: {
      latency: 0,
      num_matches: 2,
      matches: [
        {
          id: '1',
          distance: 0.8,
          post: {
            title: 'title1',
            body: 'body1',
            tags: ['tag1', 'tag2'],
          },
        },
        {
          id: '2',
          distance: 0.7,
          post: {
            title: 'title2',
            body: 'body2',
            tags: ['tag1', 'tag2'],
          },
        },
      ],
    },
    suggestions: [],
    searchTerm: '',
    error: null,
    status: StatusTypes.Success,
    infocus: false,
  };

  /**
   * Test suite for the selectSearchResult selector.
   */
  describe('selectSearchResult', () => {
    it('should select the search state', () => {
      const result = selectSearchResult.projector(initialState);
      expect(result?.matches.length).toEqual(2);
      expect(result?.matches[1].id).toEqual('2');
    });
  });

  /**
   * Test suite for the selectLoadingStatus selector.
   */
  describe('selectLoadingStatus', () => {
    it('should select status, boolean is status type loading', () => {
      const result = selectLoadingStatus.projector(initialState);
      expect(result).toEqual(false);
    });
  });
});
