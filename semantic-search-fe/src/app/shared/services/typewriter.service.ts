import { Injectable } from '@angular/core';
import { Observable, concat, from, interval, of } from 'rxjs';
import {
  concatMap,
  delay,
  ignoreElements,
  map,
  repeat,
  switchMap,
  take,
} from 'rxjs/operators';

interface TypeParams {
  word: string;
  speed: number;
  backwards?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class TypewriterService {
  /**
   * Generates an observable to type a word.
   * @param params - The typing parameters.
   * @returns An observable representing the typing effect.
   */
  private generateTypingEffect({
    word,
    speed,
    backwards = false,
  }: TypeParams): Observable<string> {
    return interval(speed).pipe(
      map((x) =>
        backwards
          ? word.substring(0, word.length - x)
          : word.substring(0, x + 1),
      ),
      take(word.length),
    );
  }

  /**
   * Combines typing and deleting effects to create a complete typewriter effect.
   * @param word - The string to type and delete.
   * @param typingSpeed - The speed of typing.
   * @param typingPause - The pause after typing.
   * @param deleteSpeed - The speed of deleting.
   * @param deletePause - The pause after deleting.
   * @returns An observable representing the complete typewriter effect.
   */
  private generateTypewriterEffect(
    word: string,
    typingSpeed: number,
    typingPause: number,
    deleteSpeed: number,
    deletePause: number,
  ) {
    return concat(
      this.generateTypingEffect({ word, speed: typingSpeed }),
      of('').pipe(delay(typingPause), ignoreElements()),
      this.generateTypingEffect({ word, speed: deleteSpeed, backwards: true }),
      of('').pipe(delay(deletePause), ignoreElements()),
    );
  }

  /**
   * Creates a typewriter effect for an array of texts.
   * @param texts$ - An observable emitting an array of texts.
   * @param typingSpeed - The speed of typing.
   * @param typingPause - The pause after typing.
   * @param deleteSpeed - The speed of deleting.
   * @param deletePause - The pause after deleting.
   * @returns An observable representing the typewriter effect.
   */
  getTypewriterEffect(
    texts$: Observable<string[]>,
    typingSpeed: number = 60,
    typingPause: number = 1200,
    deleteSpeed: number = 30,
    deletePause: number = 300,
  ) {
    return texts$.pipe(
      switchMap((texts) =>
        from(texts).pipe(
          concatMap((text) =>
            this.generateTypewriterEffect(
              text,
              typingSpeed,
              typingPause,
              deleteSpeed,
              deletePause,
            ),
          ),
          repeat(1000), // Repeat the typewriter effect for demonstration (adjust as needed).
        ),
      ),
    );
  }
}
