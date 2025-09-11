import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../decorators/FormDecorator';
import ControlledLexicalEditor from '@/components/Shared/Controlled/ControlledLexicalEditor';

const meta: Meta<typeof ControlledLexicalEditor> = {
  title: 'Components/Controlled/ControlledLexicalEditor',
  component: ControlledLexicalEditor,
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <FormDecorator>
        <Story />
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
      description: 'Editor label',
    },
    isRequired: {
      control: 'boolean',
      description: 'Whether the field is required',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the editor is disabled',
    },
    placeholder: {
      control: 'text',
      description: 'Editor placeholder text',
    },
    height: {
      control: 'text',
      description: 'Height of the editor (e.g., "200px", "10rem")',
    },
    isAdvanced: {
      control: 'boolean',
      description: 'Whether to show advanced editor features',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledLexicalEditor>;

export const Default: Story = {
  args: {
    name: 'lexicalField',
    label: 'Rich Text Editor',
    placeholder: 'Start typing...',
  },
};

export const Required: Story = {
  args: {
    name: 'lexicalField',
    label: 'Required Rich Text',
    placeholder: 'This field is required',
    isRequired: true,
  },
};

export const Disabled: Story = {
  args: {
    name: 'lexicalField',
    label: 'Disabled Editor',
    placeholder: 'This editor is disabled',
    disabled: true,
  },
};

export const WithCustomHeight: Story = {
  args: {
    name: 'lexicalField',
    label: 'Custom Height Editor',
    placeholder: 'This editor has a custom height',
    height: '200px',
  },
};

export const AdvancedEditor: Story = {
  args: {
    name: 'lexicalField',
    label: 'Advanced Editor',
    placeholder: 'This editor has advanced features',
    isAdvanced: true,
  },
};

export const WithPreContent: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ 
          lexicalField: '<p>This is some <strong>pre-filled</strong> content with <em>formatting</em>.</p>' 
        }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'lexicalField',
    label: 'Pre-filled Content',
    placeholder: 'Editor with pre-filled content',
  },
};

export const LargeEditor: Story = {
  args: {
    name: 'lexicalField',
    label: 'Large Editor',
    placeholder: 'This is a large editor for longer content',
    height: '300px',
  },
};
