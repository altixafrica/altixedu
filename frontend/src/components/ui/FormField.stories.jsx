import { useState } from 'react';
import { FormField, SelectField, TextareaField } from './form-field';

export default {
  title: 'Components/FormField',
  component: FormField,
  tags: ['autodocs'],
};

export const BasicInput = {
  args: {
    label: 'First Name',
    name: 'firstName',
    placeholder: 'Enter your first name',
    required: true,
  },
};

export const InputWithHelper = {
  args: {
    label: 'Email Address',
    name: 'email',
    type: 'email',
    placeholder: 'your.email@example.com',
    helperText: 'We\'ll never share your email with anyone else',
    required: true,
  },
};

export const InputWithValidation = {
  render: (args) => {
    const [value, setValue] = useState('');

    const emailValidator = (val) => {
      if (!val) return 'Email is required';
      if (!/\S+@\S+\.\S+/.test(val)) return 'Please enter a valid email';
      return '';
    };

    return (
      <FormField
        {...args}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        validator={emailValidator}
      />
    );
  },
  args: {
    label: 'Email',
    name: 'email',
    type: 'email',
    placeholder: 'test@example.com',
    required: true,
  },
};

export const PasswordInput = {
  args: {
    label: 'Password',
    name: 'password',
    type: 'password',
    placeholder: 'Enter a strong password',
    helperText: 'At least 8 characters',
    required: true,
  },
};

export const Select = {
  args: {
    label: 'Grade Level',
    name: 'gradeLevel',
    options: [
      { value: 'jss1', label: 'JSS 1' },
      { value: 'jss2', label: 'JSS 2' },
      { value: 'jss3', label: 'JSS 3' },
      { value: 'sss1', label: 'SSS 1' },
      { value: 'sss2', label: 'SSS 2' },
      { value: 'sss3', label: 'SSS 3' },
    ],
    required: true,
  },
  render: (args) => <SelectField {...args} />,
};

export const Textarea = {
  args: {
    label: 'Comments',
    name: 'comments',
    placeholder: 'Enter your comments here...',
    helperText: 'Maximum 500 characters',
  },
  render: (args) => <TextareaField {...args} />,
};

export const WithError = {
  args: {
    label: 'Username',
    name: 'username',
    placeholder: 'username',
    error: 'Username is already taken',
    required: true,
  },
};

export const WithSuccess = {
  args: {
    label: 'Username',
    name: 'username',
    placeholder: 'available_username',
    value: 'available_username',
    success: true,
    required: true,
  },
};

export const Disabled = {
  args: {
    label: 'School Name',
    name: 'schoolName',
    value: 'Atlas College',
    disabled: true,
  },
};
