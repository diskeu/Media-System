def build_verification_mail(user_name):    
    verification_mail = f"""
    <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding:20px; text-align:center; background-color:#007BFF; color:#ffffff; font-size:24px; font-weight:bold;">
                                Media-System
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:30px; color:#333333; font-size:16px; line-height:1.5;">
                                <p>Dear {user_name},</p>
                                <p>
                                    An Media-System account using this email address has been created. 
                                    If this was not you, please contact
                                    <a href="mailto:marvinmagmud@gmail.com" style="color:#007BFF; text-decoration:none;" target="_blank">support@media_system.com</a>.
                                </p>
                                <p>To confirm this was you, please click the button below:</p>
                                
                                <!-- Button -->
                                <p style="text-align:center; margin:30px 0;">
                                    <a href="https://deine-seite.com/confirm?token=12345" 
                                    style="display:inline-block; padding:14px 28px; font-size:16px; font-weight:bold; color:#ffffff; background-color:#007BFF; text-decoration:none; border-radius:6px; border:1px solid #007BFF;"
                                    target="_blank" 
                                    aria-label="Confirm your email for Media-System">
                                    Confirm Email
                                    </a>
                                </p>

                                <p>Best regards,</p>
                                <p>Media-System</p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px; text-align:center; font-size:12px; color:#777777; background-color:#f4f4f4;">
                                &copy; 2026 Media-System.at. All rights reserved.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    """
    return verification_mail