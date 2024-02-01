import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-darkmode',
  templateUrl: './darkmode.component.html',
  styleUrls: ['./darkmode.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DarkmodeComponent {
  changeTheme(theme: string): void {
    document.documentElement.classList.remove('light');
    document.documentElement.classList.remove('dark');
    switch (theme) {
      case 'dark':
        document.documentElement.classList.add('dark');
        localStorage['theme'] = 'dark';
        break;
      case 'light':
        document.documentElement.classList.add('light');
        localStorage['theme'] = 'light';
        break;
      default:
        document.documentElement.classList.add(
          window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light',
        );
        delete localStorage['theme'];
        break;
    }
  }
}
