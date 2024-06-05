# **AWS Account Setup**
# **Creating an AWS account**

Creating an AWS account is a fairly straightforward process and is documented on the AWS site at this URL:

[https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html)

An alternate resource that provides step-by-step tutorial on AWS account creation is available at:

[https://aws.amazon.com/getting-started/guides/setup-environment/module-one/#](https://aws.amazon.com/getting-started/guides/setup-environment/module-one/#)

You can follow any of the above URLs to create an AWS account and skip this recipe. Or you can follow instructions in this recipe to create an AWS account.

Let's continue with our AWS account creation process. 



1. Navigate to [https://aws.amazon.com/](https://aws.amazon.com/)  and click on the button with label ‘Create an AWS Account’.
    
![1  CreateAWSAccount](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/911c8bc5-b9f0-4a73-9e02-9eaa915506e1)

2. Fill in Root user email address email id and AWS account name text boxes. Click Verify Email Address Button.
![2  SignupForAWSAccount](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/0114fc54-b2f9-4b3c-9ab4-f346676752c3)

3. AWS will send you a code to the root email id. Supply that code in the next step and click the Verify Email button.
![3  VerifyEmail](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/31ddc447-bfce-432e-8a13-450cc2e3ac98)

4. In this step, create your root login password and click on the Continue button. Please provide a strong password for your root login. 

Tip: There are certain operations that can only be performed with root login and so please make sure you have always have access to this email id. Refer to this link for more details: [https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-tasks.html](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-tasks.html)

![4  SupplyPassword](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/47aeb896-842c-4827-a0ac-8e8354063c15)

5. In this step, specify that your AWS account usage type will be Personal, provide your contact information (name and address), accept AWS customer agreement and click Continue button.

![5  ProvideContactInfo](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/a124964b-8d2d-49f5-a1f6-288e2b7af104)

6.  In this step, provide credit card payment information along with a billing address. Click the Verify and Continue button.

![6  ProvideCreditCardInfo](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/ba78ab5b-2675-4bc9-af9c-4a6063eebf1c)

7. Provide a mobile phone number for verification along with Capcha. Click the Send SMS Button.

![7  VerifyIdentity](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/405c4b06-92e8-4e29-b6b6-86db8cba650f)

8. In the next step, you will get the option to select an AWS support plan. Please leave the default as Basic Support and click the Complete sign up button.

![8  SelectSupportPlan](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/46e36599-7d67-44bb-8422-94e8cb14e5a6)

Helpful Tip:
Please take a look at the link below to review features of different AWS Support Plans.
[https://aws.amazon.com/premiumsupport/plans/](https://aws.amazon.com/premiumsupport/plans/)

Also, please keep in mind that you can create a billing support case under the free basic support. If you have a question related to AWS charges, please make use of this feature.

**Important**: Even though you are done with AWS account creation, I strongly recommend that you add multi-factor authentication to your root email login. This will ensure you supply an additional authentication code (in addition to your email and password) each time you try to login to your AWS account as the root user. Please note that the root email user is authorized to perform all actions in your AWS account and so multi-factor authentication adds an additional layer of security. Once MFA is enabled, you need to supply an additional code to authenticate with AWS and login.

Tip: MFA or multi-factor authentication is a technique that requires users to authenticate with additional secret information in addition to the login credentials. That additional MFA code can be supplied by a hardware device or via a software or virtual device. 

Your MFA device can be a hardware device or you can use a virtual or software based device for multi-factor authentication. One of the most popular devices is Google Authenticator which we will use in the next recipe. 

# **Configure Root Account Credentials**

1. Review the list of MFA devices supported by AWS.

    [https://aws.amazon.com/iam/features/mfa/](https://aws.amazon.com/iam/features/mfa/)

2. Install the Google Authenticator App from Google Play Store or App Store on your mobile device.
3. Navigate to aws.amazon.com and click on the Sign in to Console Button.
4. Select the Root User option and supply your root email id. Click the Next button.
5. In the next step, supply your password to login to your AWS account.
6. Once you are logged in, click on the Search textbox at the left hand top of the landing page, type “IAM” and select the IAM service.

![IAM](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/549ec5f8-a175-4614-b408-94196c69b22d)

On the IAM dashboard, you will see a message that recommends adding MFA to your root credentials.
![AddMFA](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/7e834cb9-a388-4799-8a0a-d033aea8fb06)
Click Add MFA button

7. Switch to the Google Authenticator App on your mobile device, click the ‘+’ button and select the Scan a QR Code option.
8. Switch back to the IAM dashboard, supply device name and leave the MFA device option to ‘Authenticator app’. Click the Next button.
![Screenshot 2024-06-05 at 12 11 14 AM](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/b4a88b2d-c183-4796-a0c5-983bc17cf6ec)
9. Click the Show QR Code link and scan the QR code in the authenticator app on your mobile device.

![ShowQRCode](https://github.com/bpb-aws-book/bpb-aws-book/assets/171321045/4afff6ac-506d-4077-9357-35f1c01699eb)

Enter MFA Codes 1 and 2 that are displayed on your mobile device and click the Add MFA button. 

From this point onwards, you will need to supply root user email and password and the MFA code that displays in your authenticator app.

Congratulations, you have created your AWS account and configured MFA on root credentials. Log out from AWS and login again with your root credentials and MFA code to your AWS Account.

Tip: It is recommended that you do not login to your AWS account with root credentials unless you need to perform any operations that can only be executed by root credentials. We will create IAM users later and not use root credentials after this chapter.



