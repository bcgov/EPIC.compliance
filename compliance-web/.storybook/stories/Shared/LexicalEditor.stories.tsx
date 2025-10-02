import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import {
  Box,
  Typography,
  Button,
  FormControl,
  FormLabel,
  Switch,
  TextField,
} from "@mui/material";
import LexicalEditor from "@/components/Shared/LexicalEditor/LexicalEditor";
import { EditorState, LexicalEditor as Editor } from "lexical";
import { MentionData } from "@/components/Shared/LexicalEditor/LexicalUtils";

// Sample mention data
const sampleMentions: MentionData[] = [
  { id: 1, name: "John Doe", imageUrl: "https://via.placeholder.com/32" },
  { id: 2, name: "Jane Smith", imageUrl: "https://via.placeholder.com/32" },
  { id: 3, name: "Bob Johnson", imageUrl: "https://via.placeholder.com/32" },
  { id: 4, name: "Alice Brown", imageUrl: "https://via.placeholder.com/32" },
  { id: 5, name: "Charlie Wilson", imageUrl: "https://via.placeholder.com/32" },
];

// Demo component showing different editor configurations
const LexicalEditorDemo = () => {
  const [editorState, setEditorState] = useState<EditorState | null>(null);
  const [editor, setEditor] = useState<Editor | null>(null);
  const [isAdvanced, setIsAdvanced] = useState(false);
  const [isDisabled, setIsDisabled] = useState(false);
  const [isRequired, setIsRequired] = useState(false);
  const [height, setHeight] = useState("200px");
  const [label, setLabel] = useState("Editor Label");
  const [placeholder, setPlaceholder] = useState("Enter your text here...");
  const [errorMsg, setErrorMsg] = useState("");
  const [defaultHtml, setDefaultHtml] = useState("");

  const handleEditorChange = (
    newEditorState: EditorState,
    newEditor: Editor
  ) => {
    setEditorState(newEditorState);
    setEditor(newEditor);
  };

  const getEditorContent = () => {
    if (editor) {
      editor.getEditorState().read(() => {
        const root = editor.getEditorState()._nodeMap.get("root");
        console.log("Editor content:", root);
      });
    }
  };

  const setSampleContent = () => {
    const sampleHtml = `
      <h1>Sample Document</h1>
      <p>This is a <strong>sample document</strong> with various formatting options.</p>
      <ul>
        <li>Bullet point 1</li>
        <li>Bullet point 2</li>
        <li>Bullet point 3</li>
      </ul>
      <p>You can also use <em>italic text</em> and <u>underlined text</u>.</p>
      <blockquote>
        This is a blockquote example.
      </blockquote>
    `;
    setDefaultHtml(sampleHtml);
  };

  const setTableContent = () => {
    const tableHtml = `
      <h2>Sample Table</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Department</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Doe</td>
            <td>28</td>
            <td>Engineering</td>
          </tr>
          <tr>
            <td>Jane Smith</td>
            <td>32</td>
            <td>Marketing</td>
          </tr>
        </tbody>
      </table>
    `;
    setDefaultHtml(tableHtml);
  };

  const clearContent = () => {
    setDefaultHtml("");
  };

  const showError = () => {
    setErrorMsg("This is a sample error message");
    setTimeout(() => setErrorMsg(""), 3000);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Lexical Editor Examples
      </Typography>
      <Typography variant="body1" paragraph>
        This comprehensive example demonstrates the LexicalEditor component with
        various configurations and features.
      </Typography>

      {/* Controls */}
      <Box sx={{ mb: 3, p: 2, border: "1px solid #e0e0e0", borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          Editor Controls
        </Typography>
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 2 }}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Advanced Mode</FormLabel>
            <Switch
              checked={isAdvanced}
              onChange={(e) => setIsAdvanced(e.target.checked)}
            />
          </FormControl>
          <FormControl component="fieldset">
            <FormLabel component="legend">Disabled</FormLabel>
            <Switch
              checked={isDisabled}
              onChange={(e) => setIsDisabled(e.target.checked)}
            />
          </FormControl>
          <FormControl component="fieldset">
            <FormLabel component="legend">Required</FormLabel>
            <Switch
              checked={isRequired}
              onChange={(e) => setIsRequired(e.target.checked)}
            />
          </FormControl>
        </Box>
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 2 }}>
          <TextField
            label="Height"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            size="small"
            sx={{ width: 120 }}
          />
          <TextField
            label="Label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            size="small"
            sx={{ width: 150 }}
          />
          <TextField
            label="Placeholder"
            value={placeholder}
            onChange={(e) => setPlaceholder(e.target.value)}
            size="small"
            sx={{ width: 200 }}
          />
        </Box>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button variant="outlined" onClick={setSampleContent} size="small">
            Set Sample Content
          </Button>
          <Button variant="outlined" onClick={setTableContent} size="small">
            Set Table Content
          </Button>
          <Button variant="outlined" onClick={clearContent} size="small">
            Clear Content
          </Button>
          <Button variant="outlined" onClick={showError} size="small">
            Show Error
          </Button>
          <Button variant="outlined" onClick={getEditorContent} size="small">
            Get Content
          </Button>
        </Box>
      </Box>

      {/* Editor */}
      <LexicalEditor
        label={label}
        placeholder={placeholder}
        defaultHtml={defaultHtml}
        height={height}
        isAdvanced={isAdvanced}
        isRequired={isRequired}
        disabled={isDisabled}
        errorMsg={errorMsg}
        mentionsList={sampleMentions}
        onChange={handleEditorChange}
        name="demo-editor"
      />

      {/* Editor State Info */}
      {editorState && (
        <Box sx={{ mt: 2, p: 2, backgroundColor: "#f5f5f5", borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Editor State Info:
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Editor is {editor ? "initialized" : "not initialized"}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

// Basic editor demo
const BasicEditorDemo = () => {
  const handleEditorChange = (newEditorState: EditorState) => {
    // Handle editor changes if needed
    console.log("Editor state changed:", newEditorState);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Basic Editor
      </Typography>
      <Typography variant="body1" paragraph>
        A simple text editor with basic formatting options.
      </Typography>

      <LexicalEditor
        label="Basic Editor"
        placeholder="Start typing your text here..."
        onChange={handleEditorChange}
        name="basic-editor"
      />
    </Box>
  );
};

// Advanced editor demo
const AdvancedEditorDemo = () => {
  const handleEditorChange = (newEditorState: EditorState) => {
    // Handle editor changes if needed
    console.log("Editor state changed:", newEditorState);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Advanced Editor
      </Typography>
      <Typography variant="body1" paragraph>
        An advanced editor with table support, alignment options, and more
        formatting features.
      </Typography>

      <LexicalEditor
        label="Advanced Editor"
        placeholder="Start typing with advanced features..."
        isAdvanced={true}
        height="300px"
        onChange={handleEditorChange}
        name="advanced-editor"
      />
    </Box>
  );
};

// Editor with mentions demo
const MentionsEditorDemo = () => {
  const handleEditorChange = (newEditorState: EditorState) => {
    // Handle editor changes if needed
    console.log("Editor state changed:", newEditorState);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Editor with Mentions
      </Typography>
      <Typography variant="body1" paragraph>
        An editor with mention functionality. Type @ to see mention suggestions.
      </Typography>

      <LexicalEditor
        label="Editor with Mentions"
        placeholder="Type @ to mention someone..."
        mentionsList={sampleMentions}
        height="250px"
        onChange={handleEditorChange}
        name="mentions-editor"
      />
    </Box>
  );
};

// Editor with default content demo
const DefaultContentDemo = () => {
  const handleEditorChange = (newEditorState: EditorState) => {
    // Handle editor changes if needed
    console.log("Editor state changed:", newEditorState);
  };

  const defaultHtml = `
    <h1>Welcome to the Editor</h1>
    <p>This editor comes with <strong>pre-loaded content</strong> that you can edit.</p>
    <ul>
      <li>You can modify this content</li>
      <li>Add new paragraphs</li>
      <li>Change formatting</li>
    </ul>
    <p>Try editing this text to see how it works!</p>
  `;

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Editor with Default Content
      </Typography>
      <Typography variant="body1" paragraph>
        An editor that starts with pre-loaded content.
      </Typography>

      <LexicalEditor
        label="Editor with Default Content"
        placeholder="Start typing..."
        defaultHtml={defaultHtml}
        height="300px"
        onChange={handleEditorChange}
        name="default-content-editor"
      />
    </Box>
  );
};

// Disabled editor demo
const DisabledEditorDemo = () => {
  const handleEditorChange = (newEditorState: EditorState) => {
    // Handle editor changes if needed
    console.log("Editor state changed:", newEditorState);
  };

  const defaultHtml = `
    <h2>Disabled Editor</h2>
    <p>This editor is <strong>disabled</strong> and cannot be edited.</p>
    <p>The content is read-only and the toolbar is hidden.</p>
  `;

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Disabled Editor
      </Typography>
      <Typography variant="body1" paragraph>
        A disabled editor that shows content but cannot be edited.
      </Typography>

      <LexicalEditor
        label="Disabled Editor"
        placeholder="This editor is disabled"
        defaultHtml={defaultHtml}
        disabled={true}
        height="200px"
        onChange={handleEditorChange}
        name="disabled-editor"
      />
    </Box>
  );
};

// Error state demo
const ErrorStateDemo = () => {
  const handleEditorChange = (newEditorState: EditorState) => {
    // Handle editor changes if needed
    console.log("Editor state changed:", newEditorState);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Editor with Error State
      </Typography>
      <Typography variant="body1" paragraph>
        An editor showing an error state with validation message.
      </Typography>

      <LexicalEditor
        label="Editor with Error"
        placeholder="This editor has an error"
        errorMsg="This field is required and must contain at least 10 characters"
        isRequired={true}
        height="200px"
        onChange={handleEditorChange}
        name="error-editor"
      />
    </Box>
  );
};

const meta: Meta<typeof LexicalEditor> = {
  title: "Shared/LexicalEditor",
  component: LexicalEditor,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    (Story) => (
      <div style={{ width: "100%", height: "100vh" }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof LexicalEditor>;

export const InteractiveDemo: Story = {
  render: () => <LexicalEditorDemo />,
};

export const BasicEditor: Story = {
  render: () => <BasicEditorDemo />,
};

export const AdvancedEditor: Story = {
  render: () => <AdvancedEditorDemo />,
};

export const MentionsEditor: Story = {
  render: () => <MentionsEditorDemo />,
};

export const DefaultContentEditor: Story = {
  render: () => <DefaultContentDemo />,
};

export const DisabledEditor: Story = {
  render: () => <DisabledEditorDemo />,
};

export const ErrorStateEditor: Story = {
  render: () => <ErrorStateDemo />,
};

export const CustomHeightEditor: Story = {
  render: () => {
    const handleEditorChange = (newEditorState: EditorState) => {
      // Handle editor changes if needed
      console.log("Editor state changed:", newEditorState);
    };

    return (
      <Box sx={{ padding: "20px" }}>
        <Typography variant="h6" gutterBottom>
          Custom Height Editor
        </Typography>
        <Typography variant="body1" paragraph>
          An editor with a custom height of 400px.
        </Typography>

        <LexicalEditor
          label="Custom Height Editor"
          placeholder="This editor has a custom height..."
          height="400px"
          isAdvanced={true}
          onChange={handleEditorChange}
          name="custom-height-editor"
        />
      </Box>
    );
  },
};

export const RequiredEditor: Story = {
  render: () => {
    const handleEditorChange = (newEditorState: EditorState) => {
      // Handle editor changes if needed
      console.log("Editor state changed:", newEditorState);
    };

    return (
      <Box sx={{ padding: "20px" }}>
        <Typography variant="h6" gutterBottom>
          Required Editor
        </Typography>
        <Typography variant="body1" paragraph>
          A required editor with bold label indicating it's mandatory.
        </Typography>

        <LexicalEditor
          label="Required Editor"
          placeholder="This field is required..."
          isRequired={true}
          height="200px"
          onChange={handleEditorChange}
          name="required-editor"
        />
      </Box>
    );
  },
};
