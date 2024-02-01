import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  OnInit,
} from '@angular/core';
import { Observable } from 'rxjs';

import { Store } from '@ngrx/store';
import {
  selectLoadingStatus,
  selectSearchResult,
  selectSuggestions,
  selectSearchTerm,
  selectTypewriterStatus,
} from '../store/search.selectors';
import {
  inputSearch,
  loadSuggestions,
  updateSearchFocus,
  updateSearchTerm,
} from '../store/search.actions';
import { AppState } from 'src/app/app.state';
import { Result } from 'src/app/shared/types/post';
import { trigger, style, transition, animate } from '@angular/animations';
import { TypewriterService } from 'src/app/shared/services/typewriter.service';

/**
 * Search result row fading animation
 */
export const resultAnimation = {
  animate: trigger('fadeInOut', [
    transition(':enter', [
      style({ opacity: 0 }),
      animate('300ms', style({ opacity: 1 })),
    ]),
  ]),
};

/**
 * Component for handling search functionality.
 */
@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [resultAnimation.animate],
})
export class SearchComponent implements OnInit {
  // Observables for various data from the NgRx store
  public suggestions$: Observable<string[]> =
    this.store.select(selectSuggestions);
  public result$: Observable<Result | null> =
    this.store.select(selectSearchResult);
  public isLoading$: Observable<boolean> =
    this.store.select(selectLoadingStatus);
  public isTypewriter$: Observable<boolean> = this.store.select(
    selectTypewriterStatus,
  );
  public searchTerm$: Observable<string> = this.store.select(selectSearchTerm);

  // Observable for typewriter effect
  public typewriterText$: Observable<string> =
    this.typewriterService.getTypewriterEffect(this.suggestions$);

  // Flag to indicate if the page has been scrolled
  public scrolled = false;

  // Threshold for considering a long scroll
  private LONG_SCROLL = 800;

  /**
   * Construct Search Component and Inject Services
   * @param store - NgRx Store for managing state
   * @param typewriterService - Service for typewriter animation
   */
  constructor(
    private store: Store<AppState>,
    private typewriterService: TypewriterService,
  ) {}

  /**
   * Initialize the component by dispatching an action to load suggestions.
   */
  ngOnInit(): void {
    this.store.dispatch(loadSuggestions());
  }

  /**
   * Handle the search action when the user enters a search term.
   * @param searchTerm - The search term entered by the user.
   */
  inputSearch(searchTerm: string): void {
    this.store.dispatch(updateSearchTerm({ search: searchTerm }));
    this.store.dispatch(inputSearch({ searchTerm: searchTerm }));
  }

  /**
   * Request new search suggestions.
   */
  onRefresh(): void {
    this.store.dispatch(loadSuggestions());
  }

  /**
   * Update the infocus state when the search box is in or out of focus.
   */
  onSearchFocus(): void {
    this.store.dispatch(updateSearchFocus());
  }

  /**
   * Strips HTML tags from a given text.
   * @param text - The text containing HTML tags to be stripped.
   * @returns The text with HTML tags removed.
   */
  stripHTML(text: string): string {
    return text.replace(/(<([^>]+)>)/gi, '');
  }

  /**
   * Show the "go to search" button after scrolling past a certain threshold.
   */
  @HostListener('window:scroll', ['$event'])
  onWindowScroll() {
    const scroll = window.scrollY;
    if (scroll >= this.LONG_SCROLL) {
      this.scrolled = true;
    } else {
      this.scrolled = false;
    }
  }
}
