# **Asterisk as a VoIP Server**

## **Introduction**  
Asterisk is an open-source **PBX (Private Branch Exchange)** system that serves as the backbone of this VoIP project. It enables the processing of voice calls, signaling, and routing, making it a powerful solution for handling SIP (Session Initiation Protocol) communications.  

This project leverages **Asterisk** to establish a **VoIP system** with the following capabilities:  
- Configuring and managing **SIP clients** for voice communication.  
- Handling **call sessions, call routing**, and managing call flows.  
- Enabling **advanced features** such as voicemail and call recording.  

## **Asterisk Configuration Files**  
Asterisk primarily relies on three main configuration files to ensure seamless voice communication:  

### **1. `pjsip.conf` - SIP User & Network Configuration**  
The `pjsip.conf` file is responsible for setting up **SIP clients (phones)** and defining how the **Asterisk server** manages SIP-based communication.  

#### **Global Section**  
This section contains general settings for SIP communications:  
```ini
[global]
type=global
user_agent=Asterisk
protocol=udp
transport-udp=yes
bind=0.0.0.0
```
- `type=global`: Defines this section as a global setting.  
- `user_agent=Asterisk`: Identifies the server as "Asterisk" in SIP headers.  
- `protocol=udp`: Specifies **UDP** as the communication protocol for SIP signaling.  
- `bind=0.0.0.0`: Allows the server to listen for **SIP connections** on all available network interfaces.  

#### **User Configuration (SIP Endpoints)**  
Each SIP client (e.g., **User 7001, User 7002**) is assigned specific configurations in the **endpoint, authentication, and address-of-record (AOR)** sections.  

##### **Example Configuration for SIP Users 7001 & 7002**  
```ini
[7001]
type=endpoint
context=internal
disallow=all
allow=ulaw
auth=7001_auth
aors=7001_aor

[7001_auth]
type=auth
auth_type=userpass
username=7001
password=securepassword1

[7001_aor]
type=aor
max_contacts=1
```
- **Endpoint (`type=endpoint`)**: Defines a SIP user (phone).  
  - `context=internal`: Links the user to the **internal** dial plan (in `extensions.conf`).  
  - `disallow=all, allow=ulaw`: Allows **only ulaw codec** for voice communication.  
  - `auth=7001_auth`: Refers to the authentication section.  
  - `aors=7001_aor`: Links to the **address-of-record** section.  
- **Authentication (`type=auth`)**: Stores username/password for **SIP registration**.  
- **Address-of-Record (`type=aor`)**: Specifies **where the user is registered** (IP address or device).  
  - `max_contacts=1`: Limits **one device** per user.  

##### **Network & NAT Configuration**  
```ini
external_signaling_address=public_ip_or_local_ip
external_media_address=public_ip_or_local_ip
localnet=192.168.1.0/24
```
- `external_signaling_address`: The **public/local IP** used for **SIP signaling**.  
- `external_media_address`: The **IP address** handling **RTP media streams** (voice data).  
- `localnet`: Defines the **local network range** to help manage **NAT traversal** issues.  

---

### **2. `extensions.conf` - Call Routing & Dial Plan**  
The `extensions.conf` file defines **what happens when a user dials a number** (call routing).  

#### **Internal Call Routing**  
```ini
[internal]
exten => 7001,1,Answer()
 same => n,Dial(PJSIP/7001,60)
 same => n,Playback(vm-nobodyavail)
 same => n,VoiceMail(7001@main)
 same => n,Hangup()

exten => 7002,1,Answer()
 same => n,Dial(PJSIP/7002,60)
 same => n,Playback(vm-nobodyavail)
 same => n,VoiceMail(7002@main)
 same => n,Hangup()
```
- `exten => 7001,1,Answer()`: Answers incoming calls for **7001**.  
- `Dial(PJSIP/7001,60)`: Attempts to connect the call to **7001**, ringing for **60 seconds**.  
- `Playback(vm-nobodyavail)`: Plays a **voicemail prompt** if the call isn't answered.  
- `VoiceMail(7001@main)`: Sends unanswered calls to **voicemail** (configured in `voicemail.conf`).  
- `Hangup()`: Ends the call.  

#### **Voicemail Access Extensions**  
```ini
exten => 8001,1,VoiceMailMain(7001@main)
exten => 8002,1,VoiceMailMain(7002@main)
```
- `8001`: Allows **User 7001** to check their voicemail.  
- `8002`: Allows **User 7002** to check their voicemail.  

---

### **3. `voicemail.conf` - Voicemail Configuration**  
This file configures **voicemail accounts** for SIP users.  

```ini
[main]
7001 => 7001,User 7001
7002 => 7002,User 7002
```
- `7001 => 7001,User 7001`:  
  - User **7001** has a **voicemail box**.  
  - The **password** is `7001`.  
- `7002 => 7002,User 7002`: Same configuration for **User 7002**.  

If **User 7002 doesn’t answer**, the call is **forwarded to voicemail**, where the caller can leave a message.  
User **7002 can retrieve their voicemail** by dialing `8002`.  

---

## **How It All Works**  
### **1. SIP Registration (Client Login)**  
- Users **configure their softphone** (e.g., Zoiper, Linphone, or hardware SIP phones).  
- Phones send a **registration request** to **Asterisk**.  
- Asterisk **validates the credentials** using `pjsip.conf` and registers the user.  

### **2. Making a Call**  
- User **7001 dials 7002**.  
- Asterisk checks `extensions.conf` under **[internal]** context.  
- Finds **Dial(PJSIP/7002,60)** and routes the call to **7002**.  

### **3. Voice Data Transmission (RTP Protocol)**  
- Once connected, **voice packets** are exchanged using the **RTP (Real-time Transport Protocol)**.  
- The **localnet setting** in `pjsip.conf` ensures NAT traversal is handled correctly.  

### **4. Voicemail Handling**  
- If **User 7002 doesn’t answer**, the call is sent to **voicemail (7002@main)**.  
- The caller leaves a message, stored in the **voicemail system**.  
- Later, **User 7002 can retrieve messages** by dialing `8002`.  

---

## **Conclusion**  
This setup enables a **basic but fully functional VoIP system** using **Asterisk**. 🚀

