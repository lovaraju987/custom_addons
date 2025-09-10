/* @odoo-module */

import { discussSidebarCategoriesRegistry } from "@mail/discuss/core/web/discuss_sidebar_categories";
import { patch } from "@web/core/utils/patch";
import { DiscussAppCategory } from "@mail/core/common/discuss_app_category_model";
import { compareDatetime } from "@mail/utils/common/misc";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { DiscussSidebarCategories } from '@mail/discuss/core/web/discuss_sidebar_categories';


discussSidebarCategoriesRegistry.add(
    "WpChannels",
    {
//        predicate: (store) => store.discuss.WpChannels.threads.some((thread) => thread?.is_pinned),
        value: (store) => store.discuss.WpChannels,
     },
    { sequence: 30 }
);


// CHANGES FOR SORTING
patch(DiscussAppCategory.prototype, {

    /**
     * @param {import("models").Thread} t1
     * @param {import("models").Thread} t2
     */

    sortThreads(t1, t2) {
        if (this.id === "WpChannels") {
            return (
                compareDatetime(t2.lastInterestDateTime, t1.lastInterestDateTime) || t2.id - t1.id
            );
        }
        return super.sortThreads(t1, t2);
    },


});

patch(DiscussSidebarCategories.prototype,{
    setup(){
        super.setup()
         this.rpc = useService("rpc");
         this.orm = useService("orm");
         this.company = this.env.services.company.activeCompanyIds;
         this.wpchannel = this.categories.find((categ) => categ.value(this.store).id == "WpChannels")
         this.FbChannels = this.categories.find((categ) => categ.value(this.store).id == "FbChannels")
         this.InstaChannels = this.categories.find((categ) => categ.value(this.store).id == "InstaChannels")

    },

    async onClickUpdateMessageLimit(categoryID) {
        let default_limit = await this.orm.call('res.users', 'get_limit_show', []);
        if(categoryID == 'WpChannels') {
            let limit = this.env.services.user.context.wplimit ? this.env.services.user.context.wplimit + default_limit.show :  default_limit.show + default_limit.default_show
            this.env.services.user.updateContext({'wplimit': limit})
        }else if(categoryID == 'FbChannels') {
            let limit = this.env.services.user.context.fblimit ? this.env.services.user.context.fblimit + default_limit.show :  default_limit.show + default_limit.default_show
            this.env.services.user.updateContext({'fblimit': limit})
        }else if(categoryID == 'InstaChannels'){
            let limit = this.env.services.user.context.inslimit ? this.env.services.user.context.inslimit + default_limit.show :  default_limit.show + default_limit.default_show
            this.env.services.user.updateContext({'inslimit': limit})
        }
        var self = this;
    //        var init_messaging_temp = await this.env.services["mail.messaging"].initialize();
        var temp = await this.rpc("/mail/init_messaging",{ context: this.env.services.user.context });
        // Filter channels based on active company
        const activeCompanyChannels = temp.channels.filter(channel => {
            return channel.company_id ===this.company[0]; // Assuming the channel has a company_id field.
        });

        for (const cust_channel of activeCompanyChannels) {
            await self.threadService.fetchChannel(cust_channel.id);
        }
    },

//    async onClickShowLess(categoryID) {
//        var temp = await this.rpc("/mail/init_messaging",{ context: this.env.services.user.context });
//            for (const cust_channel of temp.channels) {
//                await self.threadService.fetchChannel(cust_channel.id)
//            }
//            const wpChannels = temp.channels.filter(channel => channel.channel_type === 'WpChannels');
//    },
});
