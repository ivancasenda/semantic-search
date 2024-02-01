import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import {
  searchPosts,
  searchPostsSuccess,
  searchPostsFailure,
  inputSearch,
  loadSuggestions,
  loadSuggestionsFailure,
  loadSuggestionsSuccess,
} from './search.actions';
import { SearchService } from '../services/search.service';
import { asyncScheduler, of } from 'rxjs';
import {
  switchMap,
  map,
  catchError,
  debounceTime,
  distinctUntilChanged,
  filter,
} from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';

/**
 * Effects for handling search-related actions.
 */
@Injectable()
export class SearchEffects {
  constructor(
    private actions$: Actions,
    private searchService: SearchService,
  ) {}

  /**
   * Effect to handle loading suggestions.
   */
  loadSuggestions$ = createEffect(() =>
    this.actions$.pipe(
      ofType(loadSuggestions),
      switchMap(() =>
        this.searchService.fetchSuggestions().pipe(
          map((suggestions) =>
            loadSuggestionsSuccess({ suggestions: suggestions }),
          ),
          catchError((err: HttpErrorResponse) =>
            of(loadSuggestionsFailure({ error: err.error })),
          ),
        ),
      ),
    ),
  );

  /**
   * Effect to handle input search with debouncing and filtering.
   * @param debounce - The debounce time for input search. Default is 500ms.
   * @param scheduler - The scheduler for debouncing. Default is asyncScheduler.
   */
  inputSearch$ = createEffect(
    () =>
      ({ debounce = 500, scheduler = asyncScheduler } = {}) =>
        this.actions$.pipe(
          ofType(inputSearch),
          map((action) => action.searchTerm),
          debounceTime(debounce, scheduler), // Wait 500 ms
          distinctUntilChanged(), // Ignore if searchTerm didn't change
          filter((searchTerm) => searchTerm.length >= 3), // Ignore if searchTerm length < 3
          switchMap((searchTerm) =>
            of(searchPosts({ searchTerm: searchTerm })),
          ),
        ),
  );

  /**
   * Effect to handle searching posts when a searchPosts action is dispatched.
   */
  searchPosts$ = createEffect(() =>
    this.actions$.pipe(
      ofType(searchPosts),
      map((action) => action.searchTerm),
      switchMap((searchTerm) =>
        // Call the fetchPosts method, convert it to an observable
        this.searchService.fetchPosts(searchTerm).pipe(
          // Take the returned value and return a new success action containing the posts
          map((result) => searchPostsSuccess({ result: result })),
          // Or... if it errors return a new failure action containing the error
          catchError((err: HttpErrorResponse) =>
            of(searchPostsFailure({ error: err.error })),
          ),
        ),
      ),
    ),
  );
}
