import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../decorators/FormDecorator';
import ControlledAutoComplete from '@/components/Shared/Controlled/ControlledAutoComplete';

// Sample data for stories
interface Option {
  id: number;
  name: string;
  category: string;
}

const sampleOptions: Option[] = [
  { id: 1, name: 'Option 1', category: 'Category A' },
  { id: 2, name: 'Option 2', category: 'Category A' },
  { id: 3, name: 'Option 3', category: 'Category B' },
  { id: 4, name: 'Option 4', category: 'Category B' },
  { id: 5, name: 'Option 5', category: 'Category C' },
];

const meta: Meta<typeof ControlledAutoComplete<Option>> = {
  title: 'Components/Controlled/ControlledAutoComplete',
  component: ControlledAutoComplete,
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <FormDecorator>
        <div style={{ width: '100%', minWidth: '200px' }}>
          <Story />
        </div>
      </FormDecorator>
    ),
  ],
  argTypes: {
    name: {
      control: 'text',
      description: 'Form field name',
    },
    label: {
      control: 'text',
      description: 'Field label',
    },
    placeholder: {
      control: 'text',
      description: 'Field placeholder',
    },
    multiple: {
      control: 'boolean',
      description: 'Whether multiple selection is allowed',
    },
    isRequired: {
      control: 'boolean',
      description: 'Whether the field is required',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the field is disabled',
    },
    isSortOptions: {
      control: 'boolean',
      description: 'Whether to sort options alphabetically',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    name: 'autocompleteField',
    label: 'Select Option',
    placeholder: 'Choose an option...',
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};

export const Multiple: Story = {
  args: {
    name: 'autocompleteField',
    label: 'Select Multiple Options',
    placeholder: 'Choose multiple options...',
    multiple: true,
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};

export const Required: Story = {
  args: {
    name: 'autocompleteField',
    label: 'Required Selection',
    placeholder: 'This field is required',
    isRequired: true,
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};

export const Disabled: Story = {
  args: {
    name: 'autocompleteField',
    label: 'Disabled Field',
    placeholder: 'This field is disabled',
    disabled: true,
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};

export const WithSorting: Story = {
  args: {
    name: 'autocompleteField',
    label: 'Sorted Options',
    placeholder: 'Options are sorted alphabetically',
    isSortOptions: true,
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};

export const WithBadges: Story = {
  args: {
    name: 'autocompleteField',
    label: 'Options with Badges',
    placeholder: 'Options show category badges',
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
    renderOptionBadge: (option) => ({
      label: option.category,
      color: 'default' as const,
    }),
  },
};

export const WithPreSelected: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ autocompleteField: sampleOptions[0] }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'autocompleteField',
    label: 'Pre-selected Option',
    placeholder: 'Option is pre-selected',
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};

export const WithMultiplePreSelected: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ autocompleteField: [sampleOptions[0], sampleOptions[2]] }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'autocompleteField',
    label: 'Multiple Pre-selected',
    placeholder: 'Multiple options pre-selected',
    multiple: true,
    options: sampleOptions,
    getOptionLabel: (option) => option.name,
    isOptionEqualToValue: (option, value) => option.id === value.id,
  },
};
