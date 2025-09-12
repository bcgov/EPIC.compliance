import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../../decorators/FormDecorator';
import ControlledRadioButtonGroup from '@/components/Shared/Controlled/ControlledRadioButtonGroup';

const meta: Meta<typeof ControlledRadioButtonGroup> = {
  title: 'Shared/Controlled/ControlledRadioButtonGroup',
  component: ControlledRadioButtonGroup,
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
    options: {
      control: 'object',
      description: 'Array of radio button options',
    },
    fontSize: {
      control: 'select',
      options: ['small', 'medium'],
      description: 'Font size of the radio buttons',
    },
    direction: {
      control: 'select',
      options: ['row', 'column'],
      description: 'Direction of the radio button layout',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledRadioButtonGroup>;

const sampleOptions = [
  { id: 'option1', name: 'Option 1' },
  { id: 'option2', name: 'Option 2' },
  { id: 'option3', name: 'Option 3' },
];

export const Default: Story = {
  args: {
    name: 'radioField',
    options: sampleOptions,
  },
};

export const ColumnLayout: Story = {
  args: {
    name: 'radioField',
    options: sampleOptions,
    direction: 'column',
  },
};

export const SmallFont: Story = {
  args: {
    name: 'radioField',
    options: sampleOptions,
    fontSize: 'small',
  },
};

export const WithPreSelected: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ radioField: 'option2' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'radioField',
    options: sampleOptions,
  },
};

export const ManyOptions: Story = {
  args: {
    name: 'radioField',
    options: [
      { id: 'opt1', name: 'First Option' },
      { id: 'opt2', name: 'Second Option' },
      { id: 'opt3', name: 'Third Option' },
      { id: 'opt4', name: 'Fourth Option' },
      { id: 'opt5', name: 'Fifth Option' },
      { id: 'opt6', name: 'Sixth Option' },
    ],
  },
};

