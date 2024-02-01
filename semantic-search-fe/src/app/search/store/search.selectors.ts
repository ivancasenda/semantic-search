import { createSelector } from '@ngrx/store';
import { AppState } from 'src/app/app.state';
import { SearchState, StatusTypes } from './search.reducers';

/**
 * Selector function to retrieve the entire search state from the global state.
 * @param state - The global application state.
 * @returns The search state.
 */
export const selectSearch = (state: AppState) => state.search;

/**
 * Selector function to retrieve the search result from the search state.
 * @param state - The search state.
 * @returns The search result.
 */
export const selectSearchResult = createSelector(
  selectSearch,
  (state: SearchState) => state.result,
);

/**
 * Selector function to determine if the search operation is currently in a loading state.
 * @param state - The search state.
 * @returns `true` if the search operation is loading; otherwise, `false`.
 */
export const selectLoadingStatus = createSelector(
  selectSearch,
  (state: SearchState) => state.status == StatusTypes.Loading,
);

/**
 * Selector function to determine if the typewriter effect should be active.
 * @param state - The search state.
 * @returns `true` if the search term is empty and the search input is not in focus; otherwise, `false`.
 */
export const selectTypewriterStatus = createSelector(
  selectSearch,
  (state: SearchState) => !state.searchTerm && !state.infocus,
);

/**
 * Selector function to retrieve the list of search suggestions from the search state.
 * @param state - The search state.
 * @returns The array of search suggestions.
 */
export const selectSuggestions = createSelector(
  selectSearch,
  (state: SearchState) => state.suggestions,
);

/**
 * Selector function to retrieve the current search term from the search state.
 * @param state - The search state.
 * @returns The current search term.
 */
export const selectSearchTerm = createSelector(
  selectSearch,
  (state: SearchState) => state.searchTerm,
);
