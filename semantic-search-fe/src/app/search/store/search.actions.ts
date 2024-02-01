import { createAction, props } from '@ngrx/store';
import { Result } from 'src/app/shared/types/post';

/**
 * Action to update the search term in the Search Page.
 */
export const updateSearchTerm = createAction(
  '[Search Page] Update Search Term',
  props<{ search: string }>(),
);

/**
 * Action to update the search focus in the Search Page.
 */
export const updateSearchFocus = createAction(
  '[Search Page] Update Search Focus',
);

/**
 * Action to trigger loading suggestions in the Search Page.
 */
export const loadSuggestions = createAction('[Search Page] Load Suggestions');

/**
 * Action dispatched when suggestions loading is successful.
 */
export const loadSuggestionsSuccess = createAction(
  '[Search Page] Suggestion Load Success',
  props<{ suggestions: string[] }>(),
);

/**
 * Action dispatched when suggestions loading fails.
 */
export const loadSuggestionsFailure = createAction(
  '[Search Page] Suggestion Load Failure',
  props<{ error: string }>(),
);

/**
 * Action to handle input search in the Search Page.
 */
export const inputSearch = createAction(
  '[Search Page] Input Search',
  props<{ searchTerm: string }>(),
);

/**
 * Action to trigger searching posts based on the provided search term.
 */
export const searchPosts = createAction(
  '[Search Page] Search Posts',
  props<{ searchTerm: string }>(),
);

/**
 * Action dispatched when searching posts is successful.
 */
export const searchPostsSuccess = createAction(
  '[Search Page] Posts Search Success',
  props<{ result: Result }>(),
);

/**
 * Action dispatched when searching posts fails.
 */
export const searchPostsFailure = createAction(
  '[Search Page] Posts Search Failure',
  props<{ error: string }>(),
);
