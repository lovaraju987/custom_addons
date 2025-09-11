# TUS Meta WhatsApp Base - Odoo WhatsApp Integration

## Overview

**TUS Meta WhatsApp Base** is a comprehensive WhatsApp integration module for Odoo V17 Community Edition that enables seamless communication between your Odoo system and WhatsApp using Meta's Graph API (WhatsApp Business Platform Cloud API). This module provides the core foundation for WhatsApp messaging functionality in Odoo.

## Key Features

### 🚀 Core Functionality
- **WhatsApp Business API Integration** - Complete integration with Meta's Graph API v16.0
- **Bidirectional Messaging** - Send and receive WhatsApp messages directly from Odoo
- **Template Management** - Create, edit, and manage WhatsApp message templates
- **Multi-language Support** - Support for 70+ languages for international businesses
- **Media Support** - Send and receive images, videos, documents, and audio files
- **Interactive Components** - Support for buttons, lists, and carousel messages

### 📱 Message Types Supported
- **Text Messages** - Plain text with formatting support
- **Media Messages** - Images, videos, documents, audio files
- **Template Messages** - Pre-approved business templates
- **Interactive Messages** - Buttons, lists, and quick replies
- **Location Messages** - Share and receive location data
- **Contact Messages** - Share contact information

### 🏢 Business Features
- **Multi-Company Support** - Handle multiple companies and WhatsApp Business accounts
- **Multi-Provider Support** - Manage multiple WhatsApp providers
- **User Management** - Assign specific providers to users
- **Security Groups** - Role-based access control
- **Webhook Integration** - Real-time message delivery via webhooks

### 🎨 Template System
- **Visual Template Builder** - Create templates with components (header, body, footer, buttons)
- **Dynamic Variables** - Support for dynamic content using Odoo fields
- **Template Categories** - Organize templates by utility, marketing, authentication
- **Approval Workflow** - Template submission and approval process
- **Language Variants** - Multi-language template support

## Installation

### Prerequisites
- Odoo V17 Community Edition
- Python package: `phonenumbers`
- Meta WhatsApp Business Account
- WhatsApp Business API access

### Installation Steps

1. **Install Dependencies**
   ```bash
   pip install phonenumbers
   ```

2. **Download and Install Module**
   - Place the module in your Odoo addons directory
   - Update the addons list in Odoo
   - Install the module from Apps menu

3. **Install Required Modules**
   - This module depends on: `base`, `mail`, `mail_group`, `base_automation`

## Configuration

### 1. WhatsApp Business Account Setup

1. **Create Facebook Developer Account**
   - Go to [Facebook for Developers](https://developers.facebook.com/)
   - Create a new app for Business

2. **Add WhatsApp Product**
   - Add WhatsApp product to your app
   - Get your App ID and App Secret

3. **Get Access Token**
   - Generate a permanent access token
   - Note down the token, it will be needed for configuration

### 2. Odoo Configuration

1. **Navigate to Settings**
   - Go to Settings → General Settings
   - Find "WhatsApp Integration" section

2. **Configure Provider**
   - **Provider Type**: Select "Graph API"
   - **API URL**: `https://graph.facebook.com/v16.0/`
   - **Instance ID**: Your WhatsApp phone number ID
   - **Business Account ID**: Your WhatsApp Business Account ID
   - **Access Token**: Your permanent access token
   - **App ID**: Your Facebook app ID
   - **App Secret**: Your Facebook app secret

3. **Webhook Configuration**
   - Generate a verify token
   - Configure webhook URL in Facebook Developer Console
   - URL format: `https://your-domain.com/graph_tus/webhook`

### 3. Template Configuration

1. **Create Templates**
   - Go to WhatsApp → Templates
   - Create new templates with components
   - Submit for approval if required

2. **Assign to Models**
   - Link templates to specific Odoo models
   - Configure dynamic variables

## Usage

### Sending Messages

#### From Partner/Contact Form
1. Open any partner/contact record
2. Click "Send WhatsApp" button
3. Select template or compose custom message
4. Send message

#### From Other Records
- Available on models like Sale Orders, Purchase Orders, Invoices
- Use "Send WhatsApp" action
- Template content automatically populated with record data

#### Bulk Messaging
1. Select multiple records from list view
2. Use "Send WhatsApp" action
3. Choose template and send to multiple recipients

### Receiving Messages

- Incoming messages automatically create/update partner records
- Messages stored in WhatsApp History
- Integration with Odoo's mail system
- Real-time notifications

### Template Management

#### Creating Templates
1. **Basic Information**
   - Name and category
   - Language selection
   - Model association

2. **Components**
   - **Header**: Optional media or text header
   - **Body**: Main message content with variables
   - **Footer**: Optional footer text
   - **Buttons**: Call-to-action buttons

3. **Variables**
   - Use Odoo field references
   - Format: `{{field_name}}`
   - Support for related fields: `{{partner_id.name}}`

#### Template Categories
- **Utility**: Appointment reminders, delivery updates
- **Marketing**: Promotional messages, offers
- **Authentication**: OTP, verification codes

## Models and Fields

### Core Models

#### `provider` (Provider Configuration)
- **Graph API Settings**: URL, Instance ID, Business ID, Token
- **Authentication**: Bearer token configuration
- **Webhook**: Callback URL and verify token
- **User Assignment**: Multi-user support

#### `wa.template` (WhatsApp Templates)
- **Basic Info**: Name, category, language, status
- **Content**: Body HTML, model association
- **Components**: Header, body, footer, buttons
- **Variables**: Dynamic field mapping

#### `whatsapp.history` (Message History)
- **Message Details**: Content, type, direction
- **Participants**: Partner, user information
- **Status**: Delivery, read status
- **Attachments**: Media files

#### `components` (Template Components)
- **Component Types**: Header, body, footer, button
- **Content**: Text, media, interactive elements
- **Variables**: Dynamic content support

### Extended Models

#### `res.partner` (Contacts)
- **WhatsApp Integration**: Phone validation, channel management
- **Message History**: Link to WhatsApp conversations
- **Provider Assignment**: Multi-provider support

#### `res.users` (Users)
- **Provider Configuration**: Default and multiple providers
- **Access Rights**: WhatsApp-specific permissions

#### `discuss.channel` (Chat Channels)
- **WhatsApp Channels**: Special channel type for WhatsApp
- **Provider Integration**: Link to WhatsApp providers
- **Company Support**: Multi-company configuration

## API and Webhooks

### Webhook Endpoints

#### Message Webhook
- **URL**: `/graph_tus/webhook`
- **Method**: GET (verification), POST (messages)
- **Authentication**: Verify token validation

#### Message Processing
- Automatic partner creation/update
- Message history logging
- Media file handling
- Real-time notifications

### Integration Points

#### Mail System Integration
- WhatsApp messages in mail threads
- Unified communication history
- Notification system integration

#### Automation Integration
- Server actions for WhatsApp messaging
- Automated responses
- Workflow triggers

## Security

### Access Rights
- **WhatsApp User**: Basic messaging access
- **WhatsApp Manager**: Template and provider management
- **WhatsApp Admin**: Full system configuration

### Data Security
- Encrypted token storage
- Secure webhook verification
- Partner data protection

## Troubleshooting

### Common Issues

#### Authentication Errors
- Verify access token validity
- Check app permissions in Facebook Console
- Ensure webhook verification token matches

#### Message Delivery Issues
- Verify phone number format
- Check template approval status
- Validate business account status

#### Media Upload Problems
- Check file size limits (16MB for videos, 5MB for images)
- Verify supported file formats
- Ensure proper MIME type detection

### Logging and Debugging
- Enable developer mode for detailed logging
- Check webhook delivery in Facebook Console
- Monitor Odoo logs for API errors

## Advanced Configuration

### Multi-Company Setup
1. Create separate providers for each company
2. Assign users to specific providers
3. Configure company-specific templates

### Custom Template Variables
- Create computed fields for complex variables
- Use related fields for nested data access
- Implement custom template rendering

### Integration with Other Modules
- Extend partner model for custom fields
- Create automation rules for message triggers
- Develop custom wizards for specific workflows

## Development

### Extending the Module
- Inherit from base models to add functionality
- Create custom template components
- Implement additional message types

### Custom Controllers
- Extend webhook controllers for custom processing
- Add new API endpoints for external integration
- Implement custom authentication methods

## Support and Updates

### Version Information
- **Current Version**: 17.5
- **Odoo Compatibility**: V17 Community Edition
- **License**: OPL-1 (Odoo Proprietary License)

### Getting Help
- Check module documentation
- Review Odoo logs for error details
- Contact TechUltra Solutions for support

### Updates and Maintenance
- Regular updates for new WhatsApp features
- Security patches and bug fixes
- Compatibility updates for new Odoo versions

## License and Credits

**Developer**: TechUltra Solutions Private Limited  
**Website**: [www.techultrasolutions.com](https://www.techultrasolutions.com)  
**License**: OPL-1 (Odoo Proprietary License)  
**Price**: $99 USD  

This module provides enterprise-grade WhatsApp integration for businesses looking to enhance their customer communication through the world's most popular messaging platform.
