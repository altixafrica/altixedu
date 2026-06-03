import { Button } from '../src/components/ui/button';

export default {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      options: ['default', 'primary', 'secondary', 'outline', 'ghost', 'danger'],
      control: { type: 'select' }
    },
    size: {
      options: ['sm', 'md', 'lg'],
      control: { type: 'select' }
    },
    fullWidth: {
      control: { type: 'boolean' }
    },
    disabled: {
      control: { type: 'boolean' }
    },
  },
};

export const Default = {
  args: {
    children: 'Click me',
    variant: 'default',
    size: 'md',
  },
};

export const Primary = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const Secondary = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
  },
};

export const Outline = {
  args: {
    children: 'Outline Button',
    variant: 'outline',
  },
};

export const Ghost = {
  args: {
    children: 'Ghost Button',
    variant: 'ghost',
  },
};

export const Danger = {
  args: {
    children: 'Danger Button',
    variant: 'danger',
  },
};

export const Small = {
  args: {
    children: 'Small Button',
    size: 'sm',
  },
};

export const Large = {
  args: {
    children: 'Large Button',
    size: 'lg',
  },
};

export const FullWidth = {
  args: {
    children: 'Full Width Button',
    fullWidth: true,
  },
};

export const Disabled = {
  args: {
    children: 'Disabled Button',
    disabled: true,
  },
};

export const WithAriaLabel = {
  args: {
    children: '',
    ariaLabel: 'Search',
  },
};
