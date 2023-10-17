with 

ad_history as (
    select * from {{ source('facebook_ads_fivetran', 'ad_history') }}
),

renamed as (
    select
        id::string as ad_id,
        creative_id,
        name as ad_name,
        ad_set_id::string as adset_id,
        campaign_id::string as campaign_id,
        account_id::string as account_id,
        created_time,
        updated_time,
         _fivetran_synced as valid_from,
        lead(_fivetran_synced) over (partition by id order by _fivetran_synced) as valid_to
    
    from
        ad_history
)

select * from renamed
