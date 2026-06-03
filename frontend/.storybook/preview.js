import '../src/index.css';
import { ThemeProvider } from '../src/lib/theme-context';
import { ToastProvider } from '../src/lib/toast-context';

const preview = {
  parameters: {
    layout: 'padded',
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <ToastProvider>
          <Story />
        </ToastProvider>
      </ThemeProvider>
    ),
  ],
};

export default preview;
