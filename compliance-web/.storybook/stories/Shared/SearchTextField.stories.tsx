import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import SearchTextField from '../../../src/components/Shared/SearchTextField';

const meta: Meta<typeof SearchTextField> = {
  title: 'Shared/SearchTextField',
  component: SearchTextField,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: 'text',
      description: 'The current search value',
    },
    onChange: {
      action: 'changed',
      description: 'Callback fired when the search value changes',
    },
    onClear: {
      action: 'cleared',
      description: 'Callback fired when the clear button is clicked',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
    },
    showSearchIcon: {
      control: 'boolean',
      description: 'Whether to show the search icon',
    },
    showClearButton: {
      control: 'boolean',
      description: 'Whether to show the clear button when there\'s text',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the field is disabled',
    },
    variant: {
      control: { type: 'select' },
      options: ['outlined', 'filled', 'standard'],
      description: 'TextField variant',
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium'],
      description: 'TextField size',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Wrapper component to handle state for interactive stories
const SearchTextFieldWrapper = (args: any) => {
  const [value, setValue] = useState(args.value || '');
  
  return (
    <SearchTextField
      {...args}
      value={value}
      onChange={(newValue: string) => {
        setValue(newValue);
        args.onChange?.(newValue);
      }}
      onClear={() => {
        setValue('');
        args.onClear?.();
      }}
    />
  );
};

export const Default: Story = {
  render: SearchTextFieldWrapper,
  args: {
    placeholder: 'Search',
  },
};

export const WithInitialValue: Story = {
  render: SearchTextFieldWrapper,
  args: {
    value: 'Initial search text',
    placeholder: 'Search',
  },
};

export const CustomPlaceholder: Story = {
  render: SearchTextFieldWrapper,
  args: {
    placeholder: 'Search for cr entries...',
  },
};

export const MediumSize: Story = {
  render: SearchTextFieldWrapper,
  args: {
    size: 'medium',
    placeholder: 'Search',
  },
};

export const Disabled: Story = {
  render: SearchTextFieldWrapper,
  args: {
    value: 'Disabled search field',
    placeholder: 'Search',
    disabled: true,
  },
};

export const WithoutSearchIcon: Story = {
  render: SearchTextFieldWrapper,
  args: {
    placeholder: 'Search without icon',
    showSearchIcon: false,
  },
};

export const WithoutClearButton: Story = {
  render: SearchTextFieldWrapper,
  args: {
    value: 'No clear button',
    placeholder: 'Search',
    showClearButton: false,
  },
};

export const FullWidth: Story = {
  render: SearchTextFieldWrapper,
  args: {
    placeholder: 'Full width search',
    fullWidth: true,
  },
  parameters: {
    layout: 'padded',
  },
};

export const WithLabel: Story = {
  render: SearchTextFieldWrapper,
  args: {
    label: 'Search Field',
    placeholder: 'Enter search term',
  },
};

export const WithHelperText: Story = {
  render: SearchTextFieldWrapper,
  args: {
    placeholder: 'Search',
    helperText: 'Type to search through the data',
  },
};
