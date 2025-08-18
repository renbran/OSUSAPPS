/** @odoo-module **/

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * QR Code Field Widget
 * 
 * Displays QR code for payment verification with download and verify actions
 * Compatible with Odoo 17 field widget patterns
 */
export class QRCodeField extends Component {
    static template = "account_payment_final.QRCodeField";
    static props = {
        ...standardFieldProps,
        readonly: { type: Boolean, optional: true }
};

    setup() {
        this.orm = useService("orm");
        this.http = useService("http");
        this.notification = useService("notification");
        
        this.state = useState({
            qrCode: null,
            isLoading: false,
            error: null;
});

        onWillStart(async () => {
            await this.loadQRCode();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record.data.id !== this.props.record.data.id) {
                await this.loadQRCode();
            }
        });
    }

    /**
     * Load QR code from backend
     */
    async loadQRCode() {
        if (!this.props.record.resId || this.props.record.data.state === 'draft') {
            this.state.qrCode = null;
            return;
        }

        this.state.isLoading = true;
        this.state.error = null;

        try {
            const result = await this.orm.call(;
                "account.payment",
                "generate_qr_code",
                [this.props.record.resId]
            );

            if (result.success && result.qr_code) {
                this.state.qrCode = `data:image/png;base64,${result.qr_code}`;
            } else {
                this.state.error = result.message || "Failed to generate QR code";
            }
        } catch (error) {
            console.error("QR Code generation failed:", error);
            this.state.error = "An error occurred while generating QR code";
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Download QR code as PNG file
     */
    onDownloadQR() {
        if (!this.state.qrCode) return;

        try {
            const link = document.createElement('a');
            link.download = `payment_qr_${this.props.record.data.name || this.props.record.resId}.png`;
            link.href = this.state.qrCode;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            this.notification.add("QR code downloaded successfully", {
                type: "success";
});
        } catch (error) {
            console.error("Download failed:", error);
            this.notification.add("Failed to download QR code", {
                type: "danger";
});
        }
    }

    /**
     * Open QR verification portal in new tab
     */
    onVerifyQR() {
        if (!this.state.qrCode) return;

        try {
            const baseUrl = window.location.origin;
            const verifyUrl = `${baseUrl}/payment/verify?payment_id=${this.props.record.resId}`;
            
            window.open(verifyUrl, '_blank', 'noopener,noreferrer');

            this.notification.add("Verification portal opened in new tab", {
                type: "info";
});
        } catch (error) {
            console.error("Failed to open verification portal:", error);
            this.notification.add("Failed to open verification portal", {
                type: "danger";
});
        }
    }

    /**
     * Get formatted value for display
     */
    get formattedValue() {
        if (this.state.isLoading) {
            return "Generating QR Code...";
        }
        
        if (this.state.error) {
            return this.state.error;
        }
        
        if (!this.state.qrCode) {
            return "QR Code not available";
        }
        
        return null; // Will show the QR code image;
    }
}

// Register as a field widget
registry.category("fields").add("qr_code_field", QRCodeField);

/**
 * QR Code Widget for readonly/form view display
 */
export class QRCodeWidget extends Component {
    static template = "account_payment_final.QRCodeWidget";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            qrCodeUrl: null,
            isLoading: false;
});

        onWillStart(async () => {
            await this.generateQRCode();
        });
    }

    async generateQRCode() {
        if (!this.props.record?.resId) return;

        this.state.isLoading = true;
        
        try {
            const qrData = await this.orm.call(;
                "account.payment",
                "get_qr_verification_url",
                [this.props.record.resId]
            );
            
            this.state.qrCodeUrl = qrData.qr_code_url;
        } catch (error) {
            console.error("Failed to generate QR code:", error);
        } finally {
            this.state.isLoading = false;
        }
    }
}

// Register the widget for use in reports/readonly views
registry.category("fields").add("qr_code_widget", QRCodeWidget);

