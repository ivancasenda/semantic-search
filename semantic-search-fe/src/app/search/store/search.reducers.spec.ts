import * as fromReducer from './search.reducers';
import {
  searchPosts,
  searchPostsFailure,
  searchPostsSuccess,
} from './search.actions';

import { Result } from 'src/app/shared/types/post';

/**
 * Test suite for the SearchReducer.
 */
describe('SearchReducer', () => {
  /**
   * Initial state for testing the search reducer.
   */
  const initialState: fromReducer.SearchState = {
    result: null,
    searchTerm: '',
    suggestions: [],
    error: null,
    status: fromReducer.StatusTypes.Pending,
    infocus: false,
  };

  /**
   * Test suite for an unknown action.
   */
  describe('unkown action', () => {
    /**
     * Test case: should return the default state.
     */
    it('should return the default state', () => {
      const action = {
        type: 'Unknown',
      };
      const state = fromReducer.searchReducer(initialState, action);

      expect(state).toBe(initialState);
    });
  });

  /**
   * Test suite for the searchPosts action.
   */
  describe('searchPosts action', () => {
    it('should return state with loading status and other property unchanged', () => {
      const action = searchPosts({ searchTerm: 'Test' });
      const state = fromReducer.searchReducer(initialState, action);

      expect(state.status).toEqual(fromReducer.StatusTypes.Loading);
      expect(state.result).toBe(initialState.result);
      expect(state.error).toBe(initialState.error);
    });
  });

  /**
   * Test suite for the searchPostsSuccess action.
   */
  describe('searchPostsSuccess', () => {
    it('should retrieve all posts and update state posts and status', () => {
      const searchPostsResult: Result = {
        latency: 0,
        num_matches: 1,
        matches: [
          {
            id: '1',
            distance: 0.8,
            post: {
              title: 'test',
              body: 'test',
              tags: ['tag1', 'tag2'],
            },
          },
        ],
      };
      const action = searchPostsSuccess({ result: searchPostsResult });
      const state = fromReducer.searchReducer(initialState, action);

      expect(state.result).toBe(searchPostsResult);
      expect(state.status).toEqual(fromReducer.StatusTypes.Success);
    });
  });

  /**
   * Test suite for the searchPostsFailure action.
   */
  describe('searchPostsFailure', () => {
    it('should return state with error message and error status', () => {
      const errorMsg = 'test error';
      const action = searchPostsFailure({ error: errorMsg });
      const state = fromReducer.searchReducer(initialState, action);

      const expectedState = {
        result: null,
        suggestions: [],
        searchTerm: '',
        error: errorMsg,
        status: fromReducer.StatusTypes.Error,
        infocus: false,
      };
      expect(state).toEqual(expectedState);
    });
  });
});
