import type { Meta, StoryObj } from "@storybook/react";
import { Typography } from "@mui/material";
import ParagraphWithReadMore from "@/components/Shared/ParagraphWithReadMore";

const meta: Meta<typeof ParagraphWithReadMore> = {
  title: "Shared/ParagraphWithReadMore",
  component: ParagraphWithReadMore,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
  argTypes: {
    maxHeight: {
      control: "number",
      description: "Maximum height before showing read more",
    },
    expand: {
      control: "boolean",
      description: "Whether to expand by default",
    },
    isFormatted: {
      control: "boolean",
      description: "Whether the content is formatted HTML",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

const longText = `This is a very long paragraph that contains a lot of text and will definitely exceed the maximum height limit set for the component. It includes multiple sentences and detailed information that would normally require scrolling or expanding to read in full. The component should automatically detect when the content exceeds the specified height and show a "Read More" link to allow users to expand and view the complete text. This functionality is particularly useful for displaying summaries, descriptions, or any content that might be too lengthy for the available space.`;

const shortText = `This is a short paragraph that should not trigger the read more functionality.`;

const htmlContent = `<p>This is <strong>formatted HTML content</strong> with <em>various styling</em> and <a href="#">links</a> that should be properly rendered when the <code>isFormatted</code> prop is set to true.</p><p>It can contain multiple paragraphs and complex formatting that needs to be preserved when displayed to the user.</p>`;

export const Default: Story = {
  args: {
    maxHeight: 100,
    renderTypography: <Typography variant="body1">{longText}</Typography>,
  },
};

export const ShortContent: Story = {
  args: {
    maxHeight: 100,
    renderTypography: <Typography variant="body1">{shortText}</Typography>,
  },
};

export const Expanded: Story = {
  args: {
    maxHeight: 100,
    expand: true,
    renderTypography: <Typography variant="body1">{longText}</Typography>,
  },
};

export const CustomHeight: Story = {
  args: {
    maxHeight: 150,
    renderTypography: <Typography variant="body1">{longText}</Typography>,
  },
};

export const FormattedContent: Story = {
  args: {
    maxHeight: 100,
    isFormatted: true,
    renderTypography: <div dangerouslySetInnerHTML={{ __html: htmlContent }} />,
  },
};

export const VeryLongContent: Story = {
  args: {
    maxHeight: 80,
    renderTypography: (
      <Typography variant="body1">
        {longText} {longText} {longText}
      </Typography>
    ),
  },
};
